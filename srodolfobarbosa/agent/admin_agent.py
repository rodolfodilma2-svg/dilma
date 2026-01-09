"""AdminAgent

Utilities for privileged administrative operations using ADMIN_GH_TOKEN.
This module is intended to be used by maintainers or by the NEXO agent when
configured with an administrative token stored securely (e.g., in Actions
secrets or local .env file). It intentionally requires explicit invocation
and includes safeguards (no-op if no token).
"""
from __future__ import annotations

import json
import os
from typing import Dict, Optional

import urllib.request


class AdminAgent:
    def __init__(self, token: Optional[str] = None, repo: Optional[str] = None):
        # token can be passed directly or read from env var ADMIN_GH_TOKEN
        self.token = token or os.environ.get("ADMIN_GH_TOKEN")
        self.repo = repo or os.environ.get("GITHUB_REPOSITORY")

    def _request(self, method: str, path: str, data: Optional[Dict] = None):
        if not self.token:
            raise RuntimeError("ADMIN_GH_TOKEN not set; cannot perform admin operations")
        if not self.repo:
            raise RuntimeError("GITHUB_REPOSITORY not set; cannot perform admin operations")
        owner, repo_name = self.repo.split("/")
        url = f"https://api.github.com{path}"
        headers = {"Authorization": f"token {self.token}", "Accept": "application/vnd.github+json"}
        body = None
        if data is not None:
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def apply_branch_protection(
        self,
        branch: str = "main",
        required_status_checks: Optional[Dict] = None,
        required_pull_request_reviews: Optional[Dict] = None,
        enforce_admins: bool = True,
    ) -> Dict:
        """Apply branch protection rules to a branch. Returns the API response.

        Example of required_status_checks: {"strict": True, "contexts": ["CI"]}
        Example of required_pull_request_reviews: {"dismiss_stale_reviews": True, "require_code_owner_reviews": True, "required_approving_review_count": 1}
        """
        if required_status_checks is None:
            required_status_checks = {"strict": True, "contexts": ["CI"]}
        if required_pull_request_reviews is None:
            required_pull_request_reviews = {
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": True,
                "required_approving_review_count": 1,
            }
        path = f"/repos/{self.repo}/branches/{branch}/protection"
        payload = {
            "required_status_checks": required_status_checks,
            "enforce_admins": enforce_admins,
            "required_pull_request_reviews": required_pull_request_reviews,
            "restrictions": None,
        }
        return self._request("PUT", path, data=payload)

    def get_branch_protection(self, branch: str = "main") -> Dict:
        path = f"/repos/{self.repo}/branches/{branch}/protection"
        return self._request("GET", path)

    def enable_auto_merge(self, pull_request_node_id: str, merge_method: str = "SQUASH") -> Dict:
        # Uses GraphQL mutation to enable auto-merge on a PR
        if not self.token:
            raise RuntimeError("ADMIN_GH_TOKEN not set")
        graphql_url = "https://api.github.com/graphql"
        mutation = {
            "query": "mutation enableAutoMerge($input: EnablePullRequestAutoMergeInput!){ enablePullRequestAutoMerge(input: $input){clientMutationId} }",
            "variables": {"input": {"pullRequestId": pull_request_node_id, "mergeMethod": merge_method}},
        }
        headers = {"Authorization": f"bearer {self.token}", "Accept": "application/vnd.github+json", "Content-Type": "application/json"}
        req = urllib.request.Request(graphql_url, data=json.dumps(mutation).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
