from databricks.sdk import WorkspaceClient
from databricks.sdk.service import workspace
import getpass

w = WorkspaceClient()

w.secrets.create_scope(scope="adzuna")

w.secrets.put_secret(
    scope="adzuna",
    key="app-id",
    string_value=getpass.getpass(
        "Paste your Adzuna App ID: "
    ),
)

w.secrets.put_secret(
    scope="adzuna",
    key="app-key",
    string_value=getpass.getpass(
        "Paste your Adzuna App Key: "
    ),
)

w.secrets.put_acl(
    scope="adzuna",
    principal="users",
    permission=workspace.AclPermission.READ,
)

w.secrets.put_secret(
    scope="database",
    key="lakebase-url",
    string_value=getpass.getpass("Paste your Lakebase URL: ")
)


w.secrets.put_acl(
    scope="database",
    principal="users",
    permission=workspace.AclPermission.READ,
)

