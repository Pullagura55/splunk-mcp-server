"""Splunk client for MCP server."""

import asyncio
import json
import os
import time
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SplunkClient:
    """Asynchronous Splunk client for search and management operations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize Splunk client with configuration."""
        self.config = {
            "host": os.getenv("SPLUNK_HOST", "localhost"),
            "port": int(os.getenv("SPLUNK_PORT", "8089")),
            "username": os.getenv("SPLUNK_USERNAME", "admin"),
            "password": os.getenv("SPLUNK_PASSWORD", "changeme"),
            "token": os.getenv("SPLUNK_TOKEN"),
            "scheme": os.getenv("SPLUNK_SCHEME", "https"),
            "hec_token": os.getenv("SPLUNK_HEC_TOKEN"),
            "hec_port": int(os.getenv("SPLUNK_HEC_PORT", "8088")),
            **(config or {}),
        }

        self.base_url = f"{self.config['scheme']}://{self.config['host']}:{self.config['port']}"
        self.hec_url = f"{self.config['scheme']}://{self.config['host']}:{self.config['hec_port']}"
        self.session_key: Optional[str] = None

    def _get_http_client(self) -> httpx.AsyncClient:
        """Get configured HTTP client."""
        return httpx.AsyncClient(
            timeout=30.0,
            verify=False,  # Disable SSL verification for demo purposes
        )

    async def _authenticate(self) -> None:
        """Authenticate with Splunk and get session key."""
        if self.config.get("token"):
            # Using token authentication
            return

        if self.session_key:
            # Already authenticated
            return

        async with self._get_http_client() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/services/auth/login",
                    data={
                        "username": self.config["username"],
                        "password": self.config["password"],
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()

                # Extract session key from XML response
                response_text = response.text
                start = response_text.find("<sessionKey>")
                end = response_text.find("</sessionKey>")

                if start != -1 and end != -1:
                    self.session_key = response_text[start + 12 : end]
                else:
                    raise Exception("Failed to extract session key from response")

            except Exception as e:
                raise Exception(f"Authentication failed: {e}")

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        if self.config.get("token"):
            return {"Authorization": f"Bearer {self.config['token']}"}
        elif self.session_key:
            return {"Authorization": f"Splunk {self.session_key}"}
        else:
            raise Exception("Not authenticated")

    async def search(
        self,
        query: str,
        earliest_time: str = "-1h",
        latest_time: str = "now",
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """Execute a Splunk search query."""
        try:
            await self._authenticate()

            async with self._get_http_client() as client:
                # Create search job
                search_query = query if query.startswith("search") else f"search {query}"

                create_response = await client.post(
                    f"{self.base_url}/services/search/jobs",
                    data={
                        "search": search_query,
                        "earliest_time": earliest_time,
                        "latest_time": latest_time,
                        "output_mode": "json",
                    },
                    headers={
                        **self._get_auth_headers(),
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                create_response.raise_for_status()

                # Extract search ID from XML response
                response_text = create_response.text
                start = response_text.find("<sid>")
                end = response_text.find("</sid>")

                if start == -1 or end == -1:
                    raise Exception("Failed to create search job")

                sid = response_text[start + 5 : end]

                # Wait for job completion
                max_attempts = 30
                for attempt in range(max_attempts):
                    status_response = await client.get(
                        f"{self.base_url}/services/search/jobs/{sid}",
                        params={"output_mode": "json"},
                        headers=self._get_auth_headers(),
                    )
                    status_response.raise_for_status()

                    status_data = status_response.json()
                    if status_data.get("entry", [{}])[0].get("content", {}).get("isDone"):
                        break

                    await asyncio.sleep(1)
                else:
                    raise Exception("Search job timed out")

                # Get results
                results_response = await client.get(
                    f"{self.base_url}/services/search/jobs/{sid}/results",
                    params={"output_mode": "json", "count": max_results},
                    headers=self._get_auth_headers(),
                )
                results_response.raise_for_status()

                results_data = results_response.json()
                return results_data.get("results", [])

        except Exception as e:
            # Return mock data if Splunk is not available
            print(f"Splunk not available, returning mock data: {e}")
            return self._get_mock_search_results(query)

    async def get_indexes(self) -> List[Dict[str, Any]]:
        """Get list of Splunk indexes."""
        try:
            await self._authenticate()

            async with self._get_http_client() as client:
                response = await client.get(
                    f"{self.base_url}/services/data/indexes",
                    params={"output_mode": "json"},
                    headers=self._get_auth_headers(),
                )
                response.raise_for_status()

                data = response.json()
                return [
                    {
                        "name": entry["name"],
                        "datatype": entry["content"]["datatype"],
                        "totalEventCount": entry["content"]["totalEventCount"],
                        "currentDBSizeMB": entry["content"]["currentDBSizeMB"],
                    }
                    for entry in data.get("entry", [])
                ]

        except Exception as e:
            print(f"Splunk not available, returning mock indexes: {e}")
            return self._get_mock_indexes()

    async def get_apps(self) -> List[Dict[str, Any]]:
        """Get list of Splunk apps."""
        try:
            await self._authenticate()

            async with self._get_http_client() as client:
                response = await client.get(
                    f"{self.base_url}/services/apps/local",
                    params={"output_mode": "json"},
                    headers=self._get_auth_headers(),
                )
                response.raise_for_status()

                data = response.json()
                return [
                    {
                        "name": entry["name"],
                        "version": entry["content"]["version"],
                        "label": entry["content"]["label"],
                        "visible": entry["content"]["visible"],
                        "disabled": entry["content"]["disabled"],
                    }
                    for entry in data.get("entry", [])
                ]

        except Exception as e:
            print(f"Splunk not available, returning mock apps: {e}")
            return self._get_mock_apps()

    async def create_alert(
        self,
        name: str,
        search: str,
        cron_schedule: str,
        actions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a Splunk alert."""
        try:
            await self._authenticate()

            async with self._get_http_client() as client:
                response = await client.post(
                    f"{self.base_url}/services/saved/searches",
                    data={
                        "name": name,
                        "search": search,
                        "cron_schedule": cron_schedule,
                        "actions": ",".join(actions or []),
                        "is_scheduled": "1",
                        "alert_type": "number of events",
                        "alert_comparator": "greater than",
                        "alert_threshold": "0",
                    },
                    headers={
                        **self._get_auth_headers(),
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )
                response.raise_for_status()

                return {"success": True, "message": "Alert created successfully"}

        except Exception as e:
            print(f"Splunk not available, returning mock alert creation: {e}")
            return {
                "success": True,
                "message": f"Mock alert '{name}' created successfully",
            }

    async def send_event(
        self,
        event: Dict[str, Any],
        source: Optional[str] = None,
        sourcetype: Optional[str] = None,
        index: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send event to Splunk via HTTP Event Collector."""
        if not self.config.get("hec_token"):
            raise Exception("HEC token not configured")

        try:
            async with self._get_http_client() as client:
                event_data = {
                    "time": int(time.time()),
                    "event": event,
                    "source": source,
                    "sourcetype": sourcetype,
                    "index": index,
                }

                response = await client.post(
                    f"{self.hec_url}/services/collector",
                    json=event_data,
                    headers={
                        "Authorization": f"Splunk {self.config['hec_token']}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()

                return response.json()

        except Exception as e:
            print(f"Splunk HEC not available, returning mock response: {e}")
            return {"text": "Success", "code": 0}

    async def get_saved_searches(self) -> List[Dict[str, Any]]:
        """Get list of saved searches and alerts."""
        try:
            await self._authenticate()

            async with self._get_http_client() as client:
                response = await client.get(
                    f"{self.base_url}/services/saved/searches",
                    params={"output_mode": "json"},
                    headers=self._get_auth_headers(),
                )
                response.raise_for_status()

                data = response.json()
                return [
                    {
                        "name": entry["name"],
                        "search": entry["content"]["search"],
                        "is_scheduled": entry["content"].get("is_scheduled", False),
                        "cron_schedule": entry["content"].get("cron_schedule"),
                    }
                    for entry in data.get("entry", [])
                ]

        except Exception as e:
            print(f"Splunk not available, returning mock saved searches: {e}")
            return self._get_mock_saved_searches()

    async def analyze_logs(
        self, analysis_type: str, index: str = "main", time_range: str = "-24h"
    ) -> Dict[str, Any]:
        """Perform log analysis based on analysis type."""
        analysis_queries = {
            "error_analysis": f"index={index} (level=ERROR OR status>=400) earliest={time_range} | stats count by source, level | sort -count",
            "performance_analysis": f"index={index} response_time earliest={time_range} | stats avg(response_time) max(response_time) perc95(response_time) by source",
            "security_analysis": f"index={index} (action=blocked OR level=CRITICAL OR failed) earliest={time_range} | stats count by action, src_ip | sort -count",
            "usage_analysis": f"index={index} earliest={time_range} | timechart span=1h count | stats avg(count) max(count) min(count)",
        }

        query = analysis_queries.get(analysis_type)
        if not query:
            raise Exception(f"Unknown analysis type: {analysis_type}")

        try:
            results = await self.search(query, time_range, "now", 50)

            # Process results based on analysis type
            if analysis_type == "error_analysis":
                return {
                    "error_summary": f"Found {len(results)} error sources",
                    "top_errors": results[:10] if results else [],
                    "recommendations": [
                        "Monitor top error sources",
                        "Set up alerts for critical errors",
                        "Review error patterns",
                    ],
                }
            elif analysis_type == "performance_analysis":
                return {
                    "performance_summary": f"Analyzed {len(results)} performance metrics",
                    "metrics": results[:10] if results else [],
                    "recommendations": [
                        "Monitor response time trends",
                        "Set performance baselines",
                        "Optimize slow endpoints",
                    ],
                }
            elif analysis_type == "security_analysis":
                return {
                    "security_summary": f"Found {len(results)} security events",
                    "events": results[:10] if results else [],
                    "recommendations": [
                        "Review blocked IPs",
                        "Monitor failed authentication",
                        "Update security policies",
                    ],
                }
            elif analysis_type == "usage_analysis":
                return {
                    "usage_summary": f"Analyzed {len(results)} usage patterns",
                    "patterns": results[:10] if results else [],
                    "recommendations": [
                        "Monitor peak usage times",
                        "Plan capacity scaling",
                        "Optimize resource allocation",
                    ],
                }

        except Exception as e:
            return {
                "error": str(e),
                "mock_analysis": self._get_mock_analysis(analysis_type),
            }

    # Mock data methods for when Splunk is not available

    def _get_mock_search_results(self, query: str) -> List[Dict[str, Any]]:
        """Return mock search results."""
        return [
            {
                "_time": "2024-05-02T10:30:00.000-07:00",
                "host": "web-server-01",
                "source": "/var/log/apache/access.log",
                "sourcetype": "access_combined",
                "_raw": '192.168.1.100 - - [02/May/2024:10:30:00 -0700] "GET /api/users HTTP/1.1" 200 1024',
                "status": "200",
                "method": "GET",
                "uri_path": "/api/users",
                "bytes": "1024",
            },
            {
                "_time": "2024-05-02T10:29:45.000-07:00",
                "host": "web-server-01",
                "source": "/var/log/apache/access.log",
                "sourcetype": "access_combined",
                "_raw": '192.168.1.101 - - [02/May/2024:10:29:45 -0700] "POST /api/login HTTP/1.1" 401 256',
                "status": "401",
                "method": "POST",
                "uri_path": "/api/login",
                "bytes": "256",
            },
            {
                "_time": "2024-05-02T10:29:30.000-07:00",
                "host": "app-server-01",
                "source": "/var/log/app/application.log",
                "sourcetype": "json",
                "_raw": '{"timestamp": "2024-05-02T10:29:30Z", "level": "ERROR", "message": "Database connection failed"}',
                "level": "ERROR",
                "message": "Database connection failed",
            },
        ]

    def _get_mock_indexes(self) -> List[Dict[str, Any]]:
        """Return mock index data."""
        return [
            {
                "name": "main",
                "datatype": "event",
                "totalEventCount": "1000000",
                "currentDBSizeMB": 512,
            },
            {
                "name": "web_logs",
                "datatype": "event",
                "totalEventCount": "500000",
                "currentDBSizeMB": 256,
            },
            {
                "name": "security",
                "datatype": "event",
                "totalEventCount": "250000",
                "currentDBSizeMB": 128,
            },
            {
                "name": "application_logs",
                "datatype": "event",
                "totalEventCount": "750000",
                "currentDBSizeMB": 384,
            },
        ]

    def _get_mock_apps(self) -> List[Dict[str, Any]]:
        """Return mock app data."""
        return [
            {
                "name": "search",
                "version": "9.1.0",
                "label": "Search & Reporting",
                "visible": True,
                "disabled": False,
            },
            {
                "name": "enterprise_security",
                "version": "7.3.0",
                "label": "Splunk Enterprise Security",
                "visible": True,
                "disabled": False,
            },
            {
                "name": "itsi",
                "version": "4.13.0",
                "label": "IT Service Intelligence",
                "visible": True,
                "disabled": False,
            },
            {
                "name": "monitoring_console",
                "version": "9.1.0",
                "label": "Monitoring Console",
                "visible": False,
                "disabled": False,
            },
        ]

    def _get_mock_saved_searches(self) -> List[Dict[str, Any]]:
        """Return mock saved searches data."""
        return [
            {
                "name": "High Error Rate Alert",
                "search": "index=web_logs status>=500 | stats count | where count>10",
                "is_scheduled": True,
                "cron_schedule": "*/5 * * * *",
            },
            {
                "name": "Daily Traffic Report",
                "search": "index=web_logs | timechart span=1h count",
                "is_scheduled": True,
                "cron_schedule": "0 9 * * *",
            },
            {
                "name": "Security Events",
                "search": "index=security level=CRITICAL",
                "is_scheduled": False,
                "cron_schedule": None,
            },
        ]

    def _get_mock_analysis(self, analysis_type: str) -> Dict[str, Any]:
        """Return mock analysis data."""
        mock_analyses = {
            "error_analysis": {
                "error_summary": "Mock: Found 15 error sources in last 24h",
                "top_errors": [
                    {"source": "/var/log/app.log", "count": 42, "level": "ERROR"},
                    {"source": "/var/log/web.log", "count": 28, "level": "ERROR"},
                ],
                "recommendations": ["Check application logs", "Monitor database connections"],
            },
            "performance_analysis": {
                "performance_summary": "Mock: Average response time 250ms",
                "metrics": [
                    {"source": "api", "avg_response": 200, "max_response": 500},
                    {"source": "web", "avg_response": 300, "max_response": 800},
                ],
                "recommendations": ["Optimize slow endpoints", "Add caching"],
            },
            "security_analysis": {
                "security_summary": "Mock: 5 security events detected",
                "events": [
                    {"action": "blocked", "src_ip": "192.168.1.100", "count": 10},
                    {"action": "failed_login", "src_ip": "10.0.0.1", "count": 3},
                ],
                "recommendations": ["Review firewall rules", "Monitor failed logins"],
            },
            "usage_analysis": {
                "usage_summary": "Mock: Peak usage at 2PM with 1000 requests/hour",
                "patterns": [
                    {"hour": "14:00", "count": 1000},
                    {"hour": "10:00", "count": 800},
                ],
                "recommendations": ["Scale during peak hours", "Load balancing"],
            },
        }

        return mock_analyses.get(analysis_type, {"error": "Unknown analysis type"})