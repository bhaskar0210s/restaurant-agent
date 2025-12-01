# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Deployment script for Restaurant Agent."""

import os

import vertexai
from absl import app, flags
from dotenv import load_dotenv
# Use deployment-ready agent that uses function tools instead of MCPToolset
# MCPToolset cannot be deep copied (contains TextIOWrapper) which breaks Vertex AI deployment
from restaurant_agent.agent_deploy import root_agent
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")

flags.DEFINE_bool("list", False, "List all agents.")
flags.DEFINE_bool("create", False, "Creates a new agent.")
flags.DEFINE_bool("delete", False, "Deletes an existing agent.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])


def create() -> None:
    """Creates an agent engine for Restaurant Agent."""
    # Get backend API URL - must be a deployed URL accessible from cloud
    backend_api_url = os.getenv("BACKEND_API_URL")
    if not backend_api_url or "localhost" in backend_api_url:
        print("⚠️  WARNING: BACKEND_API_URL is not set or points to localhost.")
        print("   The backend API must be deployed and accessible from the cloud.")
        print("   Set BACKEND_API_URL to your deployed backend server URL.")
        print("   Example: https://your-backend-server-xyz.run.app/mcp")
        return

    adk_app = AdkApp(agent=root_agent, enable_tracing=True)

    remote_agent = agent_engines.create(
        adk_app,
        display_name=root_agent.name,
        requirements=[
            "google-adk (>=1.19.0)",
            "google-cloud-aiplatform[agent_engines] (>=1.91.0,!=1.92.0)",
            "google-genai (>=1.52.0,<2.0.0)",
            "python-dotenv (>=1.2.1)",
            "pydantic (>=2.10.6,<3.0.0)",
            "absl-py (>=2.2.1,<3.0.0)",
            "httpx (>=0.28.0)",
        ],
        env_vars={"BACKEND_API_URL": backend_api_url},
    )
    print(f"Created remote agent: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """Deletes an existing agent."""
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"Deleted remote agent: {resource_id}")


def list_agents() -> None:
    """Lists all deployed agents."""
    remote_agents = agent_engines.list()
    template = """
{agent.name} ("{agent.display_name}")
- Create time: {agent.create_time}
- Update time: {agent.update_time}
"""
    remote_agents_string = "\n".join(
        template.format(agent=agent) for agent in remote_agents
    )
    print(f"All remote agents:\n{remote_agents_string}")


def main(argv: list[str]) -> None:
    del argv  # unused
    load_dotenv()

    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    bucket = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    )

    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print(
            "Missing required environment variable: GOOGLE_CLOUD_STORAGE_BUCKET"
        )
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    if FLAGS.list:
        list_agents()
    elif FLAGS.create:
        create()
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    else:
        print("Unknown command. Use --list, --create, or --delete")


if __name__ == "__main__":
    app.run(main)

