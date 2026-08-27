#!/usr/bin/env python3
"""Build the provider/product/artifact/occurrence research layer.

This generator intentionally distinguishes documented product identity from deployable
compiler evidence.  It imports the provider-neutral source-class and protocol identities,
but never infers conformance from a vendor or product name.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ATLAS = ROOT.parents[1]
SOURCE_CLASSES = ATLAS / "universes/source_systems/source-classes.jsonl"
PROTOCOLS = ATLAS / "universes/connectors_protocols/protocols.jsonl"
PROTOCOL_EVIDENCE = ATLAS / "universes/connectors_protocols/evidence.jsonl"
AS_OF = "2026-08-26"
EDITION = 1


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def dump_jsonl(name: str, rows: list[dict]) -> None:
    text = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
    (ROOT / name).write_text(text)


def product(
    key: str,
    provider: str,
    name: str,
    url: str,
    classes: list[str],
    protocols: list[str] | None = None,
    version: str = "rolling-current; exact occurrence build required",
    offer_kind: str = "documented_product",
    deployment_models: list[str] | None = None,
) -> dict:
    return {
        "key": key,
        "provider": provider,
        "name": name,
        "url": url,
        "classes": classes,
        "protocols": protocols or [],
        "version": version,
        "offer_kind": offer_kind,
        "deployment_models": deployment_models or ["vendor_documented; occurrence-specific"],
    }


# Product identity and candidate surface mapping.  A class reference means “this product is a
# credible occurrence research target for this source class”; it is not a conformance claim.
PRODUCTS = [
    # Operational databases and analytical repositories.
    product("postgresql", "PostgreSQL Global Development Group", "PostgreSQL", "https://www.postgresql.org/docs/18/", ["source.operational_database.relational_transactional"], ["protocol.cp.postgresql_wire", "protocol.cp.postgresql_logical_replication"], "18.x documentation family", "open_source_release", ["self_managed", "managed_by_multiple_providers"]),
    product("cockroachdb", "Cockroach Labs", "CockroachDB", "https://www.cockroachlabs.com/docs/stable/", ["source.operational_database.distributed_relational"], ["protocol.cp.postgresql_wire"], "stable documentation; exact patch required", "commercial_and_source_available"),
    product("sqlite", "SQLite Consortium", "SQLite", "https://www.sqlite.org/docs.html", ["source.operational_database.embedded_relational"], [], "3.x; exact library build required", "public_domain_release", ["embedded"]),
    product("postgis", "PostGIS Project Steering Committee", "PostGIS", "https://postgis.net/docs/", ["source.operational_database.spatial_relational"], ["protocol.cp.postgresql_wire"], "3.x; exact extension and PostgreSQL versions required", "open_source_release"),
    product("mongodb", "MongoDB", "MongoDB", "https://www.mongodb.com/docs/manual/", ["source.operational_database.document"], ["protocol.cp.mongodb_wire"], "current manual; server compatibility and FCV required", "commercial_and_source_available"),
    product("redis", "Redis", "Redis", "https://redis.io/docs/latest/", ["source.operational_database.key_value", "source.operational_database.in_memory_cache"], ["protocol.cp.redis_resp3"], "current documentation; exact server/edition required", "commercial_and_source_available"),
    product("cassandra", "Apache Software Foundation", "Apache Cassandra", "https://cassandra.apache.org/doc/latest/", ["source.operational_database.wide_column"], ["protocol.cp.cassandra_native_v5"], "5.x documentation family", "open_source_release"),
    product("neo4j", "Neo4j", "Neo4j", "https://neo4j.com/docs/", ["source.operational_database.property_graph"], ["protocol.cp.neo4j_bolt"], "current documentation; exact edition required", "commercial_and_community"),
    product("graphdb", "Ontotext", "GraphDB", "https://graphdb.ontotext.com/documentation/", ["source.operational_database.rdf_triplestore"], ["protocol.cp.sparql11_protocol"], "current documentation; exact edition required", "commercial_product"),
    product("elasticsearch", "Elastic", "Elasticsearch", "https://www.elastic.co/docs/reference/elasticsearch", ["source.operational_database.search_index", "source.operational_database.vector_similarity_index"], ["protocol.cp.http11"], "current documentation; exact stack version required", "commercial_and_source_available"),
    product("influxdb3", "InfluxData", "InfluxDB 3", "https://docs.influxdata.com/influxdb3/", ["source.operational_database.time_series"], ["protocol.cp.http11", "protocol.cp.arrow_flight_sql"], "3.x product family; exact edition required", "commercial_and_community"),
    product("arangodb", "ArangoDB", "ArangoDB", "https://docs.arangodb.com/", ["source.operational_database.multi_model"], ["protocol.cp.http11"], "current documentation; exact release required", "commercial_and_community"),
    product("snowflake", "Snowflake", "Snowflake", "https://docs.snowflake.com/en/user-guide-intro", ["source.analytical_repository.cloud_data_warehouse"], ["protocol.cp.jdbc43", "protocol.cp.odbc43"], "rolling service; account release required", "managed_service"),
    product("iceberg", "Apache Software Foundation", "Apache Iceberg", "https://iceberg.apache.org/docs/latest/", ["source.analytical_repository.lake_table"], [], "current format documentation; table metadata version required", "open_source_release"),
    product("amazon_s3", "Amazon Web Services", "Amazon Simple Storage Service", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html", ["source.analytical_repository.raw_data_lake", "source.file_object_content.object_storage"], ["protocol.cp.s3_rest", "protocol.cp.s3_multipart"], "rolling managed service; region/account behavior required", "managed_service"),
    product("ssas", "Microsoft", "SQL Server Analysis Services", "https://learn.microsoft.com/en-us/analysis-services/ssas-overview", ["source.analytical_repository.olap_cube"], ["protocol.cp.http11"], "SQL Server edition family; exact release required", "commercial_product"),
    product("cube", "Cube Dev", "Cube", "https://cube.dev/docs/product/introduction", ["source.analytical_repository.semantic_metric_store"], ["protocol.cp.http11", "protocol.cp.postgresql_wire"], "current documentation; exact deployment required", "commercial_and_open_source"),
    product("trino", "Trino Software Foundation", "Trino", "https://trino.io/docs/current/", ["source.analytical_repository.federated_query_catalog", "source.api_remote_service.remote_query_endpoint"], ["protocol.cp.jdbc43", "protocol.cp.http11"], "current release documentation; exact version required", "open_source_release"),
    product("feast", "Linux Foundation", "Feast", "https://docs.feast.dev/", ["source.analytical_repository.feature_repository"], ["protocol.cp.http11"], "current documentation; registry/provider versions required", "open_source_release"),
    product("tiledb", "TileDB", "TileDB", "https://documentation.cloud.tiledb.com/", ["source.analytical_repository.array_database"], ["protocol.cp.http11"], "current documentation; exact array format/service build required", "commercial_and_open_source"),
    product("clickhouse", "ClickHouse", "ClickHouse", "https://clickhouse.com/docs/en/", ["source.analytical_repository.query_result_cache"], ["protocol.cp.http11", "protocol.cp.jdbc43"], "current documentation; exact server/offer required", "commercial_and_open_source"),

    # Files, object/content repositories, and generic remote service surfaces.
    product("posix_files", "The Open Group", "POSIX file interfaces", "https://pubs.opengroup.org/onlinepubs/9799919799/", ["source.file_object_content.local_or_network_filesystem"], ["protocol.cp.posix_file_io", "protocol.cp.nfs41", "protocol.cp.smb3"], "Issue 8 / 2024 profile", "normative_standard", ["local", "network_mount"]),
    product("csvw", "World Wide Web Consortium", "CSV on the Web", "https://www.w3.org/TR/tabular-data-model/", ["source.file_object_content.delimited_text_file"], [], "W3C Recommendation", "normative_standard", ["file_occurrence"]),
    product("dfsortrf", "IBM", "DFSORT fixed-record datasets", "https://www.ibm.com/docs/en/zos/3.2.0?topic=dfsort", ["source.file_object_content.fixed_width_record_file", "source.legacy_offline.fixed_record_batch_exchange"], ["protocol.cp.ebcdic_blocked_file", "protocol.cp.fixed_record_ftp"], "z/OS 3.2 documentation family", "commercial_product"),
    product("jsonlines", "Python Software Foundation", "Python JSON Lines processing profile", "https://docs.python.org/3/library/json.html", ["source.file_object_content.self_describing_row_file"], [], "Python 3 documentation; framing profile remains local", "documentation_profile"),
    product("parquet", "Apache Software Foundation", "Apache Parquet", "https://parquet.apache.org/docs/", ["source.file_object_content.columnar_analytical_file"], [], "current format documentation; file metadata required", "open_standard_and_release"),
    product("excel", "Microsoft", "Microsoft Excel workbooks", "https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-xlsx/", ["source.file_object_content.spreadsheet_workbook"], [], "MS-XLSX current published specification", "commercial_product"),
    product("xml_json", "World Wide Web Consortium", "XML and JSON document profiles", "https://www.w3.org/TR/xml/", ["source.file_object_content.xml_json_document_file"], [], "XML 1.0 plus occurrence-specific JSON profile", "normative_standard"),
    product("zip", "PKWARE", "ZIP file format", "https://support.pkware.com/pkzip/appnote", ["source.file_object_content.archive_or_package"], [], "APPNOTE current publication", "published_format"),
    product("matlab_files", "MathWorks", "MATLAB MAT-files", "https://www.mathworks.com/help/pdf_doc/matlab/matfile_format.pdf", ["source.file_object_content.binary_proprietary_file"], [], "published MAT-file format family", "commercial_product"),
    product("sterling_mft", "IBM", "Sterling File Gateway", "https://www.ibm.com/support/pages/sterling-file-gateway-documentation", ["source.file_object_content.managed_file_transfer", "source.event_messaging_cdc.edi_mailbox_gateway"], ["protocol.cp.sftp", "protocol.cp.as2", "protocol.cp.un_edifact", "protocol.cp.x12_edi"], "6.x documentation family", "commercial_product"),
    product("box", "Box", "Box Content Cloud", "https://developer.box.com/reference/", ["source.file_object_content.enterprise_content_repository"], ["protocol.cp.http11", "protocol.cp.webhook_http"], "rolling SaaS; enterprise configuration required", "managed_service"),
    product("purview_records", "Microsoft", "Microsoft Purview Records Management", "https://learn.microsoft.com/en-us/purview/records-management", ["source.file_object_content.records_archive"], ["protocol.cp.http11"], "rolling SaaS; tenant policy required", "managed_service"),
    product("sharepoint", "Microsoft", "SharePoint Online", "https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/get-to-know-the-sharepoint-rest-service", ["source.file_object_content.shared_document_workspace", "source.api_remote_service.webdav_content_api"], ["protocol.cp.http11", "protocol.cp.webdav"], "rolling SaaS; tenant build required", "managed_service"),
    product("github_api", "GitHub", "GitHub APIs", "https://docs.github.com/en/rest", ["source.api_remote_service.http_resource_api", "source.api_remote_service.graphql_query_api"], ["protocol.cp.http11", "protocol.cp.graphql_over_http", "protocol.cp.webhook_http"], "rolling SaaS and GHES editions; exact target required", "managed_and_self_managed"),
    product("dataverse", "Microsoft", "Microsoft Dataverse Web API", "https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview", ["source.api_remote_service.odata_data_service"], ["protocol.cp.odata401", "protocol.cp.odata_batch"], "rolling SaaS; tenant API version required", "managed_service"),
    product("workday_ws", "Workday", "Workday Web Services", "https://community.workday.com/sites/default/files/file-hosting/productionapi/index.html", ["source.api_remote_service.soap_web_service"], ["protocol.cp.soap12", "protocol.cp.wsdl20"], "rolling SaaS; tenant WSDL version required", "managed_service"),
    product("google_grpc", "Google", "Google Cloud APIs", "https://cloud.google.com/apis/docs/system-parameters", ["source.api_remote_service.binary_rpc_service"], ["protocol.cp.grpc", "protocol.cp.grpc_streaming"], "rolling managed APIs; service edition required", "managed_service"),
    product("salesforce_bulk", "Salesforce", "Salesforce Bulk API 2.0", "https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/", ["source.api_remote_service.bulk_export_api"], ["protocol.cp.http11"], "rolling SaaS; org API version required", "managed_service"),
    product("powerbi_export", "Microsoft", "Power BI export APIs", "https://learn.microsoft.com/en-us/rest/api/power-bi/reports/export-to-file", ["source.api_remote_service.screen_or_report_export"], ["protocol.cp.http11"], "rolling SaaS; capacity and tenant required", "managed_service"),

    # Event, messaging, CDC.
    product("kafka", "Apache Software Foundation", "Apache Kafka", "https://kafka.apache.org/documentation/", ["source.event_messaging_cdc.partitioned_append_log"], ["protocol.cp.kafka_wire", "protocol.cp.kafka_connect"], "current release documentation; broker version required", "open_source_release"),
    product("google_pubsub", "Google", "Google Cloud Pub/Sub", "https://cloud.google.com/pubsub/docs/overview", ["source.event_messaging_cdc.publish_subscribe_topic"], ["protocol.cp.grpc", "protocol.cp.http11"], "rolling service; regional feature and subscription required", "managed_service"),
    product("rabbitmq", "Broadcom", "RabbitMQ", "https://www.rabbitmq.com/docs", ["source.event_messaging_cdc.work_message_queue"], ["protocol.cp.amqp10", "protocol.cp.mqtt5", "protocol.cp.stomp12"], "current release documentation; exact server required", "commercial_and_open_source"),
    product("debezium", "Red Hat", "Debezium", "https://debezium.io/documentation/reference/stable/", ["source.event_messaging_cdc.transaction_log_cdc"], ["protocol.cp.kafka_connect"], "stable documentation; exact connector/server matrix required", "open_source_release"),
    product("eventstoredb", "Event Store", "EventStoreDB", "https://developers.eventstore.com/server/", ["source.event_messaging_cdc.event_sourced_journal"], ["protocol.cp.grpc", "protocol.cp.http11"], "current server docs; exact release required", "commercial_and_open_source"),
    product("hivemq", "HiveMQ", "HiveMQ", "https://docs.hivemq.com/hivemq/latest/user-guide/", ["source.event_messaging_cdc.mqtt_broker"], ["protocol.cp.mqtt5"], "current documentation; exact broker edition required", "commercial_product"),
    product("github_webhooks", "GitHub", "GitHub Webhooks", "https://docs.github.com/en/webhooks", ["source.event_messaging_cdc.webhook_delivery"], ["protocol.cp.webhook_http"], "rolling SaaS and GHES; exact event/version required", "managed_and_self_managed"),
    product("eventbridge", "Amazon Web Services", "Amazon EventBridge", "https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html", ["source.event_messaging_cdc.cloud_event_bus"], ["protocol.cp.http11", "protocol.cp.cloudevents10"], "rolling service; region/account required", "managed_service"),
    product("millicast", "Dolby", "Dolby.io Real-time Streaming", "https://docs.dolby.io/streaming-apis/docs", ["source.event_messaging_cdc.streaming_media_bus"], ["protocol.cp.websocket"], "rolling service; account/region required", "managed_service"),

    # Enterprise applications.
    product("sap_s4", "SAP", "SAP S/4HANA", "https://help.sap.com/docs/SAP_S4HANA_CLOUD", ["source.enterprise_application.enterprise_resource_planning", "source.enterprise_application.general_ledger_accounting", "source.enterprise_application.procure_to_pay", "source.enterprise_application.order_to_cash_billing"], ["protocol.cp.odata401", "protocol.cp.soap12", "protocol.cp.cloudevents10"], "Cloud 2608 / on-prem 2025 families; exact edition required", "managed_and_self_managed"),
    product("salesforce", "Salesforce", "Salesforce Platform", "https://developer.salesforce.com/docs/platform", ["source.enterprise_application.customer_relationship_management", "source.enterprise_application.marketing_automation"], ["protocol.cp.http11", "protocol.cp.webhook_http"], "rolling SaaS; org API version required", "managed_service"),
    product("workday", "Workday", "Workday HCM", "https://community.workday.com/sites/default/files/file-hosting/productionapi/Human_Resources/v44.0/Human_Resources.html", ["source.enterprise_application.human_resources_payroll"], ["protocol.cp.soap12"], "v44 documentation surface; tenant version required", "managed_service"),
    product("oracle_scm", "Oracle", "Oracle Fusion Cloud SCM", "https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/", ["source.enterprise_application.supply_chain_planning"], ["protocol.cp.http11", "protocol.cp.soap12"], "rolling SaaS; quarterly update required", "managed_service"),
    product("manhattan_wms", "Manhattan Associates", "Manhattan Active Warehouse Management", "https://developer.manh.com/docs/", ["source.enterprise_application.warehouse_management"], ["protocol.cp.http11"], "rolling SaaS; tenant release required", "managed_service"),
    product("oracle_otm", "Oracle", "Oracle Transportation Management", "https://docs.oracle.com/en/cloud/saas/transportation/", ["source.enterprise_application.transportation_management"], ["protocol.cp.http11"], "rolling SaaS; quarterly update required", "managed_service"),
    product("opcenter", "Siemens", "Siemens Opcenter Execution", "https://docs.sw.siemens.com/en-US/doc/282219420/PL20230428425572335", ["source.enterprise_application.manufacturing_execution"], ["protocol.cp.http11"], "product release family; exact module/version required", "commercial_product"),
    product("maximo", "IBM", "IBM Maximo Application Suite", "https://www.ibm.com/docs/en/mas-cd/continuous-delivery", ["source.enterprise_application.asset_maintenance"], ["protocol.cp.http11"], "continuous-delivery documentation; exact channel required", "commercial_product"),
    product("deltek_vantagepoint", "Deltek", "Deltek Vantagepoint", "https://help.deltek.com/product/Vantagepoint/", ["source.enterprise_application.project_professional_services"], ["protocol.cp.http11"], "current documentation; exact release required", "commercial_product"),
    product("servicenow", "ServiceNow", "ServiceNow Platform", "https://www.servicenow.com/docs/r/api-reference/rest-apis/api-rest.html", ["source.enterprise_application.it_service_management", "source.enterprise_application.customer_support_contact_center"], ["protocol.cp.http11", "protocol.cp.graphql_over_http", "protocol.cp.soap12"], "Australia release documentation; instance build required", "managed_service"),
    product("shopify", "Shopify", "Shopify Admin", "https://shopify.dev/docs/api/admin-graphql", ["source.enterprise_application.commerce_order_pos"], ["protocol.cp.graphql_over_http", "protocol.cp.webhook_http"], "versioned rolling API; shop and API version required", "managed_service"),
    product("oracle_epm", "Oracle", "Oracle Fusion Cloud EPM", "https://docs.oracle.com/en/cloud/saas/enterprise-performance-management-common/prest/", ["source.enterprise_application.enterprise_planning_performance"], ["protocol.cp.http11"], "rolling SaaS; monthly update required", "managed_service"),
    product("informatica_mdm", "Informatica", "Informatica MDM", "https://docs.informatica.com/master-data-management.html", ["source.enterprise_application.master_data_management"], ["protocol.cp.http11"], "product family; exact service/edition required", "managed_and_self_managed"),

    # Collaboration, code/DevOps, security, and telemetry.
    product("microsoft_graph_mail", "Microsoft", "Microsoft Graph Mail", "https://learn.microsoft.com/en-us/graph/api/resources/mail-api-overview", ["source.collaboration_productivity.email_mailbox"], ["protocol.cp.http11"], "v1.0 rolling SaaS; tenant/cloud required", "managed_service"),
    product("microsoft_graph_calendar", "Microsoft", "Microsoft Graph Calendar", "https://learn.microsoft.com/en-us/graph/api/resources/calendar-overview", ["source.collaboration_productivity.calendar_scheduling"], ["protocol.cp.http11"], "v1.0 rolling SaaS; tenant/cloud required", "managed_service"),
    product("microsoft_teams", "Microsoft", "Microsoft Teams Graph APIs", "https://learn.microsoft.com/en-us/graph/teams-concept-overview", ["source.collaboration_productivity.team_chat", "source.collaboration_productivity.meeting_conferencing"], ["protocol.cp.http11"], "v1.0 rolling SaaS; tenant/cloud required", "managed_service"),
    product("confluence", "Atlassian", "Confluence Cloud", "https://developer.atlassian.com/cloud/confluence/rest/v2/intro/", ["source.collaboration_productivity.wiki_knowledge_base"], ["protocol.cp.http11"], "rolling SaaS; site and API version required", "managed_service"),
    product("microsoft_forms", "Microsoft", "Microsoft Forms", "https://support.microsoft.com/en-us/forms", ["source.collaboration_productivity.forms_surveys"], ["protocol.cp.http11"], "rolling SaaS; supported export/API remains occurrence-specific", "managed_service"),
    product("microsoft_planner", "Microsoft", "Microsoft Planner Graph API", "https://learn.microsoft.com/en-us/graph/api/resources/planner-overview", ["source.collaboration_productivity.task_work_management"], ["protocol.cp.http11"], "v1.0 rolling SaaS; tenant required", "managed_service"),
    product("figma", "Figma", "Figma Platform", "https://developers.figma.com/docs/rest-api/", ["source.collaboration_productivity.whiteboard_design_workspace"], ["protocol.cp.http11", "protocol.cp.webhook_http"], "rolling SaaS; team/file entitlement required", "managed_service"),
    product("github_repos", "GitHub", "GitHub repositories and issues", "https://docs.github.com/en/rest/repos", ["source.code_devops.distributed_version_control", "source.code_devops.issue_change_tracker"], ["protocol.cp.http11"], "rolling SaaS and GHES; exact target required", "managed_and_self_managed"),
    product("github_actions", "GitHub", "GitHub Actions", "https://docs.github.com/en/actions", ["source.code_devops.ci_cd_orchestrator"], ["protocol.cp.http11", "protocol.cp.webhook_http"], "rolling SaaS and GHES; exact target required", "managed_and_self_managed"),
    product("github_packages", "GitHub", "GitHub Packages and attestations", "https://docs.github.com/en/packages", ["source.code_devops.artifact_package_registry", "source.code_devops.software_bill_of_materials"], ["protocol.cp.oci_distribution", "protocol.cp.http11"], "rolling SaaS and GHES; registry type required", "managed_and_self_managed"),
    product("kubernetes", "Cloud Native Computing Foundation", "Kubernetes API", "https://kubernetes.io/docs/reference/using-api/", ["source.code_devops.runtime_control_plane"], ["protocol.cp.http11"], "versioned API; cluster server version required", "open_source_and_managed"),
    product("terraform", "HashiCorp", "Terraform state", "https://developer.hashicorp.com/terraform/language/state", ["source.code_devops.configuration_infrastructure_state"], ["protocol.cp.http11"], "state format and backend version required", "commercial_and_source_available"),
    product("entra", "Microsoft", "Microsoft Entra ID", "https://learn.microsoft.com/en-us/graph/api/resources/identity-network-overview", ["source.security_identity.identity_directory", "source.security_identity.identity_provider_authentication"], ["protocol.cp.http11", "protocol.cp.scim2"], "rolling SaaS; tenant/cloud required", "managed_service"),
    product("cyberark", "CyberArk", "CyberArk Privilege Cloud", "https://docs.cyberark.com/privilege-cloud-standard/latest/en/content/webservices/intro.htm", ["source.security_identity.privileged_access_secrets"], ["protocol.cp.http11"], "rolling SaaS; tenant/region required", "managed_service"),
    product("okta_logs", "Okta", "Okta System Log", "https://developer.okta.com/docs/reference/system-log-query/", ["source.security_identity.security_audit_log"], ["protocol.cp.http11"], "rolling SaaS; org/engine required", "managed_service"),
    product("splunk", "Cisco", "Splunk Enterprise Security", "https://docs.splunk.com/Documentation/ES", ["source.security_identity.siem_detection_case"], ["protocol.cp.http11"], "product/release matrix required", "managed_and_self_managed"),
    product("misp", "MISP Project", "MISP", "https://www.misp-project.org/documentation/", ["source.security_identity.threat_intelligence_exchange"], ["protocol.cp.http11"], "exact release and taxonomy set required", "open_source_release"),
    product("tenable", "Tenable", "Tenable Vulnerability Management", "https://developer.tenable.com/reference/navigate", ["source.security_identity.vulnerability_exposure_management"], ["protocol.cp.http11"], "rolling SaaS; container/permissions required", "managed_service"),
    product("zeek", "Zeek Project", "Zeek", "https://docs.zeek.org/en/current/", ["source.security_identity.network_security_telemetry"], [], "current docs; exact package/version required", "open_source_release"),
    product("opentelemetry", "Cloud Native Computing Foundation", "OpenTelemetry", "https://opentelemetry.io/docs/specs/", ["source.telemetry_digital_experience.application_logs", "source.telemetry_digital_experience.application_metrics", "source.telemetry_digital_experience.distributed_traces"], ["protocol.cp.otlp", "protocol.cp.trace_context"], "specification/release versions required", "open_standard_and_release"),
    product("google_analytics", "Google", "Google Analytics Data API", "https://developers.google.com/analytics/devguides/reporting/data/v1", ["source.telemetry_digital_experience.web_product_analytics"], ["protocol.cp.http11"], "rolling SaaS; property/retention required", "managed_service"),
    product("firebase_analytics", "Google", "Google Analytics for Firebase", "https://firebase.google.com/docs/analytics", ["source.telemetry_digital_experience.mobile_product_analytics"], ["protocol.cp.http11"], "rolling SDK/service; app and SDK version required", "managed_service"),
    product("google_ad_manager", "Google", "Google Ad Manager API", "https://developers.google.com/ad-manager/api/start", ["source.telemetry_digital_experience.ad_media_measurement"], ["protocol.cp.soap12"], "versioned API; network and report semantics required", "managed_service"),

    # IoT, industrial, scientific, geo/media.
    product("californium", "Eclipse Foundation", "Eclipse Californium", "https://eclipse.dev/californium/", ["source.iot_edge.constrained_device_api"], ["protocol.cp.coap"], "exact release/profile required", "open_source_release"),
    product("azure_iot_hub", "Microsoft", "Azure IoT Hub", "https://learn.microsoft.com/en-us/azure/iot-hub/iot-concepts-and-iot-hub", ["source.iot_edge.iot_sensor_gateway", "source.iot_edge.device_twin_registry"], ["protocol.cp.mqtt5", "protocol.cp.http11"], "rolling managed service; region/tier required", "managed_service"),
    product("aws_greengrass", "Amazon Web Services", "AWS IoT Greengrass", "https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html", ["source.iot_edge.edge_buffer_store_forward"], ["protocol.cp.mqtt5"], "rolling service plus edge component versions", "managed_and_edge_runtime"),
    product("landisgyr", "Landis+Gyr", "Gridstream metering platform", "https://www.landisgyr.com/product/gridstream-connect/", ["source.iot_edge.smart_meter_gateway"], [], "commercial deployment; exact head-end/interface required", "commercial_product"),
    product("geotab", "Geotab", "MyGeotab SDK", "https://developers.geotab.com/myGeotab/apiReference/", ["source.iot_edge.vehicle_telematics"], ["protocol.cp.http11"], "rolling service; database/retention required", "managed_service"),
    product("couchbase_lite", "Couchbase", "Couchbase Lite", "https://docs.couchbase.com/couchbase-lite/current/index.html", ["source.iot_edge.mobile_offline_store"], ["protocol.cp.http11"], "exact SDK and sync gateway versions required", "commercial_and_community"),
    product("wincc", "Siemens", "SIMATIC WinCC", "https://support.industry.siemens.com/cs/document/109963091/", ["source.industrial_ot.scada_dcs"], ["protocol.cp.opcua"], "product release/patch required", "commercial_product"),
    product("prosys_opc", "Prosys OPC", "Prosys OPC UA Simulation Server", "https://prosysopc.com/products/opc-ua-simulation-server/", ["source.industrial_ot.opcua_information_server"], ["protocol.cp.opcua"], "exact release/security profile required", "commercial_and_free_tool"),
    product("simatic_s7", "Siemens", "SIMATIC S7-1500", "https://support.industry.siemens.com/cs/document/59192925/", ["source.industrial_ot.plc_controller"], ["protocol.cp.opcua"], "firmware/hardware catalog number required", "industrial_product"),
    product("aveva_pi", "AVEVA", "AVEVA PI System", "https://docs.aveva.com/bundle/pi-server", ["source.industrial_ot.industrial_historian"], ["protocol.cp.http11"], "exact PI Server/Web API versions required", "commercial_product"),
    product("desigo", "Siemens", "Desigo CC", "https://support.industry.siemens.com/cs/document/109813615/", ["source.industrial_ot.building_automation"], ["protocol.cp.bacnet"], "exact release/site profile required", "commercial_product"),
    product("abb_robot", "ABB", "ABB RobotWare", "https://developercenter.robotstudio.com/api/rwsApi/", ["source.industrial_ot.robotics_machine_controller"], ["protocol.cp.http11"], "controller/RobotWare version required", "industrial_product"),
    product("cognex", "Cognex", "Cognex VisionPro", "https://support.cognex.com/docs/vpromx_100/", ["source.industrial_ot.quality_inspection_system"], [], "exact release/camera/job required", "industrial_product"),
    product("pcs7", "Siemens", "SIMATIC PCS 7", "https://support.industry.siemens.com/cs/document/109812124/", ["source.industrial_ot.batch_process_control"], ["protocol.cp.opcua"], "exact release/site recipe profile required", "industrial_product"),
    product("spectrum_power", "Siemens", "Spectrum Power", "https://www.siemens.com/global/en/products/energy/grid-software/operation/spectrum-power.html", ["source.industrial_ot.energy_grid_control"], ["protocol.cp.iec61850", "protocol.cp.dnp3"], "commercial deployment; exact interface/profile required", "industrial_product"),
    product("labware", "LabWare", "LabWare LIMS", "https://www.labware.com/lims", ["source.scientific_research.laboratory_information_management"], ["protocol.cp.http11"], "commercial deployment; exact module/API required", "commercial_product"),
    product("thermo_instrument", "Thermo Fisher Scientific", "Thermo Scientific instrument software", "https://docs.thermofisher.com/", ["source.scientific_research.scientific_instrument"], [], "instrument/model/software version required", "scientific_product"),
    product("netcdf", "Unidata", "NetCDF", "https://docs.unidata.ucar.edu/netcdf-c/current/", ["source.scientific_research.multidimensional_scientific_file"], ["protocol.cp.netcdf", "protocol.cp.hdf5", "protocol.cp.zarr3"], "format/library version required", "open_standard_and_release"),
    product("ncbi_sra", "National Center for Biotechnology Information", "Sequence Read Archive", "https://www.ncbi.nlm.nih.gov/sra/docs/", ["source.scientific_research.genomics_sequence_repository"], ["protocol.cp.http11"], "public service; accession/release state required", "public_service"),
    product("medidata_rave", "Dassault Systèmes", "Medidata Rave EDC", "https://learn.mdsol.com/", ["source.scientific_research.clinical_research_edc"], ["protocol.cp.http11"], "rolling service; study/configuration required", "managed_service"),
    product("openfoam", "OpenFOAM Foundation", "OpenFOAM", "https://doc.cfd.direct/openfoam/user-guide-v13/", ["source.scientific_research.simulation_model_output"], [], "v13 documentation; exact solver/case required", "open_source_release"),
    product("zenodo", "CERN", "Zenodo", "https://developers.zenodo.org/", ["source.scientific_research.research_data_repository"], ["protocol.cp.http11"], "rolling public service; record/version required", "public_service"),
    product("slurm", "SchedMD", "Slurm Workload Manager", "https://slurm.schedmd.com/documentation.html", ["source.scientific_research.high_performance_job_scheduler"], ["protocol.cp.http11"], "exact server/client version required", "open_source_release"),
    product("arcgis", "Esri", "ArcGIS Feature Service", "https://developers.arcgis.com/rest/services-reference/enterprise/feature-service/", ["source.geospatial_media.gis_feature_service"], ["protocol.cp.http11", "protocol.cp.ogc_api_features", "protocol.cp.wfs20"], "exact ArcGIS/feature-service version required", "managed_and_self_managed"),
    product("copernicus", "European Space Agency", "Copernicus Data Space Ecosystem", "https://documentation.dataspace.copernicus.eu/APIs/STAC.html", ["source.geospatial_media.raster_remote_sensing_catalog"], ["protocol.cp.stac11", "protocol.cp.odata401"], "rolling public service; collection processing baseline required", "public_service"),
    product("cesium_ion", "Cesium GS", "Cesium ion", "https://cesium.com/learn/ion/rest-api/", ["source.geospatial_media.point_cloud_repository"], ["protocol.cp.http11"], "rolling service; asset pipeline/version required", "managed_service"),
    product("autodesk_acc", "Autodesk", "Autodesk Construction Cloud", "https://aps.autodesk.com/en/docs/data/v2/overview/", ["source.geospatial_media.cad_bim_repository"], ["protocol.cp.http11"], "rolling SaaS; hub/project/region required", "managed_service"),
    product("bynder", "Bynder", "Bynder DAM", "https://bynder.docs.apiary.io/", ["source.geospatial_media.image_asset_library"], ["protocol.cp.http11"], "rolling SaaS; portal/version required", "managed_service"),
    product("verint", "Verint", "Verint Interaction Recording", "https://connect.verint.com/developers/", ["source.geospatial_media.audio_recording_repository"], ["protocol.cp.http11"], "commercial deployment; exact API/module required", "commercial_product"),
    product("milestone", "Milestone Systems", "XProtect", "https://doc.developer.milestonesys.com/", ["source.geospatial_media.video_surveillance_media"], ["protocol.cp.http11", "protocol.cp.websocket"], "exact product/device/codec version required", "commercial_product"),
    product("here_location", "HERE Technologies", "HERE platform location services", "https://www.here.com/docs/", ["source.geospatial_media.mobility_location_stream"], ["protocol.cp.http11"], "rolling service; catalog/layer/region required", "managed_service"),
    product("noaa_cdo", "National Oceanic and Atmospheric Administration", "NOAA Climate Data Online", "https://www.ncei.noaa.gov/cdo-web/webservices/v2", ["source.geospatial_media.weather_environmental_observation"], ["protocol.cp.http11", "protocol.cp.sensorthings11"], "public service; dataset/station revision required", "public_service"),

    # Public/reference, regulated verticals, and legacy/offline.
    product("ckan", "Open Knowledge Foundation", "CKAN", "https://docs.ckan.org/en/latest/api/", ["source.public_reference.open_data_catalog"], ["protocol.cp.http11"], "exact site and CKAN extension/version required", "open_source_release"),
    product("ecb_sdmx", "European Central Bank", "ECB Data Portal", "https://data.ecb.europa.eu/help/api/overview", ["source.public_reference.official_statistics_exchange"], ["protocol.cp.http11"], "public service; dataset/revision required", "public_service"),
    product("umls", "National Library of Medicine", "Unified Medical Language System", "https://documentation.uts.nlm.nih.gov/rest/home.html", ["source.public_reference.reference_code_registry"], ["protocol.cp.http11"], "release/version/license required", "public_service"),
    product("companies_house", "UK Companies House", "Companies House API", "https://developer.company-information.service.gov.uk/", ["source.public_reference.government_administrative_register"], ["protocol.cp.http11"], "public service; filing/status revision required", "public_service"),
    product("rss", "RSS Advisory Board", "RSS 2.0", "https://www.rssboard.org/rss-specification", ["source.public_reference.web_feed_and_syndication"], ["protocol.cp.http11"], "RSS 2.0 profile plus feed occurrence required", "published_standard"),
    product("common_crawl", "Common Crawl Foundation", "Common Crawl", "https://commoncrawl.org/get-started", ["source.public_reference.web_crawl_snapshot"], ["protocol.cp.s3_rest", "protocol.cp.http11"], "monthly crawl index and WARC segment required", "public_service"),
    product("sec_edgar", "U.S. Securities and Exchange Commission", "EDGAR", "https://www.sec.gov/edgar/sec-api-documentation", ["source.public_reference.published_report_filing_portal", "source.regulated_vertical.regulatory_xbrl_filing"], ["protocol.cp.http11", "protocol.cp.xbrl_reporting"], "public service; filing accession and taxonomy required", "public_service"),
    product("epic", "Epic Systems", "Epic EHR FHIR APIs", "https://fhir.epic.com/Specifications", ["source.regulated_vertical.electronic_health_record", "source.regulated_vertical.pharmacy_medication_management"], ["protocol.cp.fhir_r5_rest", "protocol.cp.fhir_bulk20", "protocol.cp.hl7v2_mllp"], "customer release and enabled implementation guide required", "commercial_product"),
    product("change_healthcare", "UnitedHealth Group", "Change Healthcare Medical Network APIs", "https://developers.changehealthcare.com/", ["source.regulated_vertical.health_claims_adjudication"], ["protocol.cp.http11", "protocol.cp.x12_edi"], "product/tenant/payer contract required", "managed_service"),
    product("orthanc", "Orthanc Team", "Orthanc", "https://orthanc.uclouvain.be/book/", ["source.regulated_vertical.medical_imaging_pacs"], ["protocol.cp.dicomweb", "protocol.cp.dicom_dimse"], "exact server/plugin/version required", "open_source_release"),
    product("temenos", "Temenos", "Temenos Transact", "https://developer.temenos.com/", ["source.regulated_vertical.core_banking"], ["protocol.cp.http11"], "commercial deployment; exact product/API contract required", "commercial_product"),
    product("swift", "Swift", "Swift ISO 20022 services", "https://www.swift.com/standards/iso-20022", ["source.regulated_vertical.payments_ledger"], ["protocol.cp.iso20022_messages"], "annual standards release plus network service required", "network_service"),
    product("nasdaq_ouch", "Nasdaq", "Nasdaq OUCH order entry", "https://www.nasdaqtrader.com/content/technicalsupport/specifications/TradingProducts/OUCH5.0.pdf", ["source.regulated_vertical.trading_order_execution"], ["protocol.cp.fix_session", "protocol.cp.fixp"], "interface specification and venue rollout required", "market_infrastructure"),
    product("bloomberg_bpipe", "Bloomberg", "Bloomberg B-PIPE", "https://www.bloomberg.com/professional/product/market-data/", ["source.regulated_vertical.market_data_feed"], [], "licensed service; feed/entitlement/schema required", "commercial_service"),
    product("guidewire", "Guidewire", "Guidewire InsuranceSuite", "https://docs.guidewire.com/", ["source.regulated_vertical.insurance_policy_claims"], ["protocol.cp.http11"], "cloud/self-managed edition and API version required", "managed_and_self_managed"),
    product("amdocs", "Amdocs", "Amdocs OSS/BSS", "https://www.amdocs.com/products-services/catalog", ["source.regulated_vertical.telecom_oss_bss"], ["protocol.cp.http11", "protocol.cp.openapi32"], "commercial deployment; TM Forum/profile proof required", "commercial_product"),
    product("oracle_utilities", "Oracle", "Oracle Utilities", "https://docs.oracle.com/en/industries/energy-water/", ["source.regulated_vertical.utility_meter_billing"], ["protocol.cp.http11"], "exact product/release/utility configuration required", "commercial_product"),
    product("amos", "Swiss AviationSoftware", "AMOS", "https://www.swiss-as.com/amos/", ["source.regulated_vertical.aviation_operations_maintenance"], [], "commercial deployment; exact module/export required", "commercial_product"),
    product("gtfs_realtime", "MobilityData", "GTFS Realtime", "https://gtfs.org/documentation/realtime/reference/", ["source.regulated_vertical.rail_transit_operations"], ["protocol.cp.http11"], "feed version/agency occurrence required", "open_standard"),
    product("marine_traffic", "Kpler", "MarineTraffic API", "https://servicedocs.marinetraffic.com/", ["source.regulated_vertical.maritime_logistics_tracking"], ["protocol.cp.http11"], "licensed service; endpoint/data-plan required", "commercial_service"),
    product("veeva_qms", "Veeva Systems", "Veeva QualityOne/Vault QMS", "https://developer.veevavault.com/", ["source.regulated_vertical.pharmaceutical_quality_manufacturing"], ["protocol.cp.http11"], "rolling SaaS; vault/release/lifecycle config required", "managed_service"),
    product("tyler_justice", "Tyler Technologies", "Enterprise Justice", "https://www.tylertech.com/products/enterprise-justice", ["source.regulated_vertical.government_case_justice"], [], "commercial deployment; exact export/interface required", "commercial_product"),
    product("canvas", "Instructure", "Canvas LMS", "https://developerdocs.instructure.com/services/canvas", ["source.regulated_vertical.education_student_learning"], ["protocol.cp.http11"], "rolling SaaS/self-managed; account/API version required", "managed_and_self_managed"),
    product("arcgis_parcels", "Esri", "ArcGIS Parcel Fabric", "https://pro.arcgis.com/en/pro-app/latest/help/data/parcel-editing/what-is-parcel-fabric-.htm", ["source.regulated_vertical.property_land_cadastral"], ["protocol.cp.http11", "protocol.cp.ogc_api_features"], "exact geodatabase/service/version required", "commercial_product"),
    product("ibm_ims", "IBM", "IBM IMS and Db2 for z/OS", "https://www.ibm.com/docs/en/ims", ["source.legacy_offline.mainframe_relational_or_hierarchical"], ["protocol.cp.drda"], "exact subsystem/product version required", "commercial_product"),
    product("ibm_vsam", "IBM", "z/OS VSAM", "https://www.ibm.com/docs/en/zos/3.2.0?topic=sets-virtual-storage-access-method", ["source.legacy_offline.indexed_sequential_dataset"], ["protocol.cp.ebcdic_blocked_file"], "z/OS 3.2 documentation; dataset attributes required", "commercial_product"),
    product("ibm_tape", "IBM", "IBM TS4500 tape library", "https://www.ibm.com/docs/en/ts4500-tape-library", ["source.legacy_offline.tape_or_cold_archive"], ["protocol.cp.iscsi"], "hardware/firmware/media generation required", "hardware_product"),
    product("jes_spool", "IBM", "z/OS JES spool", "https://www.ibm.com/docs/en/zos/3.2.0?topic=jes2", ["source.legacy_offline.print_spool_report"], ["protocol.cp.tn3270e"], "z/OS/JES level and output class required", "commercial_product"),
    product("cics", "IBM", "CICS Transaction Server", "https://www.ibm.com/docs/en/cics-ts", ["source.legacy_offline.transaction_monitor"], ["protocol.cp.tn3270e"], "exact CICS TS region/version required", "commercial_product"),
    product("encrypted_media", "National Institute of Standards and Technology", "Removable-media transfer profile", "https://csrc.nist.gov/publications/detail/sp/800-111/final", ["source.legacy_offline.air_gapped_media_transfer"], [], "local governed occurrence required", "guidance_profile"),
    product("abbyy", "ABBYY", "ABBYY FineReader Engine", "https://support.abbyy.com/hc/en-us/categories/360000573680-FineReader-Engine", ["source.legacy_offline.paper_form_ocr"], [], "exact OCR engine/language/model required", "commercial_product"),
    product("odk", "Get ODK", "ODK Collect", "https://docs.getodk.org/collect-intro/", ["source.legacy_offline.manual_offline_register"], ["protocol.cp.http11"], "exact mobile app/form/server versions required", "open_source_release"),
]


ADAPTER_ROLES = [
    ("sql_snapshot_reader", "Repeatable SQL snapshot reader"), ("sql_cdc_reader", "Transactional log CDC reader"),
    ("document_snapshot_reader", "Document collection snapshot reader"), ("document_change_reader", "Document change-stream reader"),
    ("key_value_scanner", "Key/value scanner"), ("wide_column_scanner", "Wide-column partition scanner"),
    ("graph_query_reader", "Graph query reader"), ("rdf_sparql_reader", "SPARQL graph reader"),
    ("search_scroll_reader", "Search point-in-time/scroll reader"), ("time_series_range_reader", "Time-series range reader"),
    ("warehouse_query_reader", "Warehouse query reader"), ("lake_table_snapshot_reader", "Lake-table snapshot reader"),
    ("object_listing_reader", "Object listing and byte-range reader"), ("filesystem_watcher", "Filesystem enumeration/watcher"),
    ("delimited_file_reader", "Delimited-file reader"), ("fixed_record_reader", "Fixed-record reader"),
    ("row_document_reader", "Self-describing row reader"), ("columnar_reader", "Columnar analytical reader"),
    ("spreadsheet_reader", "Workbook reader"), ("archive_expander", "Archive/package expander"),
    ("content_repository_reader", "Content repository reader"), ("records_archive_reader", "Records archive reader"),
    ("http_paged_reader", "HTTP paged resource reader"), ("graphql_cursor_reader", "GraphQL cursor reader"),
    ("odata_delta_reader", "OData delta reader"), ("soap_operation_reader", "SOAP operation reader"),
    ("grpc_stream_reader", "gRPC streaming reader"), ("bulk_export_manager", "Asynchronous bulk-export manager"),
    ("report_export_reader", "Rendered report export reader"), ("append_log_consumer", "Partitioned-log consumer"),
    ("pubsub_subscriber", "Publish/subscribe subscriber"), ("queue_receiver", "Work-queue receiver"),
    ("webhook_receiver", "Authenticated webhook receiver"), ("event_bus_subscriber", "Cloud event-bus subscriber"),
    ("edi_mailbox_reader", "EDI mailbox reader"), ("email_sync_reader", "Mailbox synchronization reader"),
    ("calendar_delta_reader", "Calendar delta reader"), ("collaboration_export_reader", "Collaboration workspace reader"),
    ("git_history_reader", "Git history reader"), ("devops_event_reader", "DevOps event reader"),
    ("identity_directory_reader", "Directory/provisioning reader"), ("security_log_reader", "Security audit-log reader"),
    ("telemetry_receiver", "Telemetry protocol receiver"), ("iot_gateway_reader", "IoT gateway reader"),
    ("opcua_subscription_reader", "OPC UA subscription reader"), ("historian_reader", "Industrial historian reader"),
    ("scientific_array_reader", "Scientific multidimensional reader"), ("stac_asset_reader", "STAC asset reader"),
    ("fhir_bulk_reader", "FHIR bulk-data reader"), ("dicomweb_reader", "DICOMweb reader"),
    ("financial_message_reader", "Financial message reader"), ("mainframe_dataset_reader", "Mainframe dataset reader"),
    ("offline_media_ingester", "Governed offline-media ingester"), ("ocr_capture_reader", "OCR capture reader"),
]


INNOVATIONS = [
    ("postgres_logical_replication_failover", 2024, "PostgreSQL logical replication failover and slot synchronization", "postgresql", "replication topology and recovery proof changed"),
    ("postgres_generated_column_replication", 2025, "PostgreSQL generated-column logical replication controls", "postgresql", "schema and value-origin qualification changed"),
    ("mongodb_change_stream_expanded_events", 2022, "MongoDB expanded change-stream event surfaces", "mongodb", "event vocabulary and stable-API qualification changed"),
    ("mongodb_change_stream_preimages", 2022, "MongoDB change-stream pre/post images", "mongodb", "before-image retention and downgrade hazards became explicit"),
    ("cassandra_v5_protocol", 2024, "Cassandra 5.0 protocol and storage evolution", "cassandra", "driver/server compatibility qualification changed"),
    ("redis_resp3_adoption", 2021, "RESP3 client/server capability negotiation adoption", "redis", "type and push-message handling changed"),
    ("iceberg_rest_catalog", 2022, "Iceberg REST catalog protocol", "iceberg", "catalog binding separated from table-format identity"),
    ("iceberg_v3", 2025, "Iceberg format version 3", "iceberg", "row lineage and deletion-vector capability profiles changed"),
    ("parquet_bloom_filter_encryption", 2021, "Parquet modular encryption and bloom-filter ecosystem maturation", "parquet", "reader capability and key boundary qualification changed"),
    ("s3_express_one_zone", 2023, "S3 Express One Zone directory buckets", "amazon_s3", "endpoint, namespace, consistency, and cost profiles changed"),
    ("kafka_kraft", 2023, "Kafka KRaft production transition", "kafka", "controller identity and operational dependency topology changed"),
    ("kafka_tiered_storage", 2023, "Kafka tiered storage", "kafka", "retention, fetch path, latency, and cost evidence changed"),
    ("pubsub_exactly_once", 2022, "Google Pub/Sub exactly-once delivery option", "google_pubsub", "regional delivery receipt requirements changed"),
    ("debezium_incremental_snapshots", 2021, "Debezium incremental snapshots and signaling", "debezium", "snapshot/change handoff and chunking decisions changed"),
    ("cloudevents_sql", 2024, "CloudEvents SQL filtering", "eventbridge", "filter semantics became a separately versioned profile"),
    ("salesforce_cdc_custom_channels", 2023, "Salesforce change-event custom channel evolution", "salesforce", "event selection, replay, and retention profiles changed"),
    ("dataverse_rowversion", 2023, "Dataverse/Finance row-version change tracking", "dataverse", "deletion scope and cursor retention require new qualification"),
    ("sap_business_event_logging", 2025, "SAP S/4HANA business-event logging", "sap_s4", "event existence and field-change evidence no longer equal subscriptions"),
    ("otel_logs_stable", 2023, "OpenTelemetry Logs stable specification", "opentelemetry", "log signal conformance profile stabilized"),
    ("otel_profiles", 2025, "OpenTelemetry Profiles signal", "opentelemetry", "profiling source surface and OTLP qualification expanded"),
    ("fhir_bulk_v2", 2021, "FHIR Bulk Data Access v2", "epic", "asynchronous export, status, and file retrieval profiles changed"),
    ("fhir_r5", 2023, "FHIR Release 5", "epic", "resource and conformance identity must retain FHIR edition"),
    ("stac_1_1", 2025, "STAC 1.1.0", "copernicus", "asset metadata and extension qualification changed"),
    ("ogc_api_features_crs", 2022, "OGC API Features CRS-by-reference", "arcgis", "CRS negotiation and loss proof became explicit"),
    ("zarr_v3", 2024, "Zarr version 3", "netcdf", "chunk-grid, codec pipeline, and store capability profiles changed"),
    ("graphql_over_http", 2025, "GraphQL over HTTP specification", "github_api", "transport/profile negotiation became distinct from schema semantics"),
    ("github_artifact_attestations", 2024, "GitHub artifact attestations", "github_packages", "artifact provenance receipts became a first-class source surface"),
    ("kubernetes_watch_bookmarks", 2021, "Kubernetes watch bookmarks and resource-version recovery maturation", "kubernetes", "list/watch handoff and compaction handling changed"),
    ("snowflake_streaming_iceberg", 2026, "Snowpipe Streaming into Iceberg v3 tables", "snowflake", "streaming, table-format edition, buffering, and catalog limits require joint qualification"),
    ("okta_log_streaming", 2022, "Okta system-log streaming integrations", "okta_logs", "polling and push occurrences require distinct retention/order proofs"),
    ("copernicus_stac_1_1", 2026, "Copernicus Data Space STAC 1.1 rollout", "copernicus", "provider occurrence must preserve collection processing baseline and API rollout"),
    ("service_now_graphql", 2025, "ServiceNow GraphQL API framework exposure", "servicenow", "API profile discovery expanded beyond REST/SOAP"),
]


GAPS = [
    ("tenant_build_identity", "Rolling SaaS documentation rarely exposes the exact tenant build needed for reproducible binding."),
    ("entitlement_inventory", "Public documentation cannot prove object-, field-, event-, or export-level tenant entitlements."),
    ("regional_rollout", "Regional and sovereign-cloud feature rollout is not normalized across providers."),
    ("numerical_limits", "Limits vary by edition, tenant, contract, region, configuration, and time."),
    ("cost_and_egress", "Current contractual cost, egress, API overage, and private-link charges require occurrence evidence."),
    ("schema_discovery", "Discovery APIs may omit hidden, computed, virtual, or unauthorized fields."),
    ("field_authority", "Product-level evidence does not establish field-level system-of-record authority."),
    ("delete_semantics", "Hard delete, soft delete, tombstone, redaction, compaction, and archival are incompletely documented."),
    ("correction_finality", "Correction, reversal, settlement, and publication-revision finality remain object-specific."),
    ("snapshot_consistency", "Bulk/export completion does not prove one transactionally consistent cross-object cut."),
    ("snapshot_cdc_handoff", "Many product APIs do not publish a lossless snapshot-to-change handoff contract."),
    ("cursor_expiry", "Cursor/delta/replay token retention and expiry are often mutable and tenant-specific."),
    ("paging_under_mutation", "Stable enumeration under concurrent inserts/deletes is not proven by ordinary pagination docs."),
    ("ordering_scope", "Ordering scope across partitions, topics, entities, and subscriptions requires measurement."),
    ("duplicate_behavior", "Retry and duplicate behavior requires injected-failure tests."),
    ("write_acceptance", "Transport success is not proof of source validation, commit, or business acceptance."),
    ("destructive_write_guard", "Write/delete/industrial command surfaces require independent authorization and fail-safe proof."),
    ("identity_collision", "Cross-tenant, cross-site, recycle, merge, and natural-key collision behavior is under-documented."),
    ("timezone_calendar", "User/site calendars, DST policy, ambiguous local times, and historical timezone changes remain occurrence facts."),
    ("clock_quality", "Device/server clock synchronization, drift, and timestamp origin require observed evidence."),
    ("content_acl_versions", "Content ACL inheritance, version visibility, retention labels, and legal holds need dedicated probes."),
    ("media_fidelity", "Codec, color, sample-rate, orientation, metadata, and transcoding losses require content probes."),
    ("geo_crs_axis_order", "CRS edition, epoch, axis order, vertical datum, and reprojection loss remain under-qualified."),
    ("scientific_units_fill", "Units, fill values, calendars, chunking, and instrument calibration need dataset-specific evidence."),
    ("healthcare_profiles", "FHIR base version does not establish implementation-guide, terminology, patient identity, or authorization conformance."),
    ("financial_finality", "Authorization, clearing, settlement, cancellation, correction, and ledger posting must remain distinct."),
    ("ot_safety_boundary", "Read connectivity never authorizes commands to PLC, SCADA, robot, batch, or grid-control systems."),
    ("mainframe_encoding_layout", "EBCDIC CCSID, copybook, RECFM/LRECL, blocked records, packed decimal, and generation data require occurrence evidence."),
    ("offline_chain_of_custody", "Air-gapped and removable-media transfers need custody, malware, integrity, import, and destruction receipts."),
    ("connector_supply_chain", "Adapter release, lockfile, SBOM, license, vulnerability, support, and removal seam are not yet populated per product."),
    ("vendor_doc_freshness", "Documentation pages can change without a pinned content digest or explicit behavior-change notice."),
    ("export_and_exit", "Full-fidelity export, deletion, portability, and supplier-exit paths require destructive and scale testing."),
]


NEGATIVE_TWINS = [
    ("vendor_is_class", "Infer source semantics from vendor/product name", "Require provider-neutral class plus occurrence evidence"),
    ("product_is_offer", "Treat product identity as a managed offer", "Preserve product, offer, deployment, and endpoint identities"),
    ("docs_are_probe", "Treat official documentation as observed behavior", "Record documented and probed claims separately"),
    ("rolling_is_version", "Use latest/current as a reproducible version", "Resolve exact tenant/build or refuse reproducible binding"),
    ("protocol_is_model", "Infer object meaning from transport protocol", "Bind a separate semantic/data-model contract"),
    ("connector_is_source", "Let connector catalog define source taxonomy", "Connector satisfies source capability requirements only"),
    ("read_implies_write", "Enable writes because reads succeeded", "Qualify and authorize each write/command independently"),
    ("http_success_is_commit", "Treat HTTP success as business commit", "Verify acceptance, commit, asynchronous result, and reconciliation"),
    ("queue_ack_is_effect", "Treat broker acknowledgement as downstream effect", "Compose broker and sink-effect receipts"),
    ("export_is_snapshot", "Treat completed export as one consistent cut", "Prove cut semantics and cross-object consistency"),
    ("cursor_is_resume", "Reuse a paging cursor as CDC resume token", "Type tokens by issuer, purpose, scope, cut, retention, and expiry"),
    ("no_records_is_empty", "Map unauthorized/unsupported/inconclusive to empty", "Return a typed refusal or gap"),
    ("api_version_is_product", "Conflate API version with product release", "Retain independent product, API, schema, and connector versions"),
    ("region_is_cosmetic", "Ignore service region/sovereign cloud", "Bind exact occurrence region and rollout evidence"),
    ("limit_is_universal", "Copy a published default into every tenant", "Observe value, unit, scope, provenance, date, and failure behavior"),
    ("schema_visible_is_complete", "Treat discovered fields as complete schema", "Retain authorization and hidden/computed-field uncertainty"),
    ("delete_is_delete", "Collapse every deletion mechanism", "Model hard, soft, tombstone, redaction, TTL, compaction, hold, supersession"),
    ("timestamp_is_event_time", "Treat any timestamp as business event time", "Preserve event, commit, ingestion, publication, and observation times"),
    ("order_is_global", "Promote partition/key order to global order", "Retain ordering scope and gap behavior"),
    ("exactly_once_label", "Accept provider exactly-once label end to end", "Prove source replay, adapter checkpoint, pipeline recovery, and sink effect"),
    ("marketing_is_conformance", "Use marketing prose as a capability receipt", "Use normative docs and executed qualification only"),
    ("standard_name_is_profile", "Assume naming FHIR/FIX/OPC UA proves profile conformance", "Bind exact edition, profile, extensions, and test receipts"),
    ("file_extension_is_format", "Infer representation from filename extension", "Probe framing, magic, schema, encoding, and content"),
    ("acl_is_data_access", "Infer content visibility from repository login", "Probe object/field/version/attachment ACLs"),
    ("encrypted_is_authorized", "Treat encrypted transport as permission", "Separate channel protection, identity, policy, and object authorization"),
    ("same_product_same_tenant", "Reuse proof across tenants/sites", "Scope receipts to endpoint occurrence and configuration digest"),
    ("managed_means_operated", "Assume managed service removes consumer duties", "Bind shared-responsibility and operational evidence"),
    ("retry_is_safe", "Retry every failed operation", "Classify refusal, idempotency key, acceptance ambiguity, and compensation"),
    ("table_name_is_identity", "Use mutable object name as durable identity", "Bind catalog/object IDs and rename/recycle behavior"),
    ("export_is_exit", "Treat one export endpoint as supplier portability", "Prove coverage, fidelity, history, ACLs, metadata, cost, and deletion"),
]


PROBES = [
    "product_and_build_identity", "endpoint_and_region_identity", "object_discovery", "field_schema_and_hidden_fields",
    "object_key_stability", "authority_and_field_ownership", "repeatable_snapshot_cut", "pagination_under_mutation",
    "snapshot_to_change_handoff", "change_resume_after_disconnect", "cursor_expiry_and_rebootstrap", "delete_modes",
    "update_before_after_images", "transaction_boundaries", "cross_object_atomicity", "ordering_scope",
    "gap_and_duplicate_injection", "correction_and_retraction", "time_axes_and_clock_origin", "timezone_dst_calendar",
    "authentication_mechanism", "object_field_authorization", "tenant_isolation", "network_private_endpoint",
    "encryption_and_key_boundary", "audit_event_coverage", "rate_limit_envelope", "page_and_payload_limits",
    "concurrency_and_timeout", "retention_and_replay", "cost_egress_and_overage", "schema_evolution_compatibility",
    "content_acl_version_hold", "media_fidelity_roundtrip", "geo_crs_axis_epoch", "scientific_units_fill_calendar",
    "health_profile_terminology", "financial_finality_reversal", "ot_read_only_safety", "mainframe_ccsid_copybook",
    "offline_custody_malware_integrity", "write_acceptance_and_idempotency", "destructive_command_guard", "export_exit_fidelity",
]


def main() -> None:
    source_classes = load_jsonl(SOURCE_CLASSES)
    protocols = load_jsonl(PROTOCOLS)
    protocol_evidence = load_jsonl(PROTOCOL_EVIDENCE)
    class_ids = {row["class_id"] for row in source_classes}
    protocol_ids = {row["protocol_id"] for row in protocols}

    providers = {}
    sources = []
    upstream_evidence_map = {}
    for item in protocol_evidence:
        sid = "source.occurrence.upstream." + item["evidence_id"].removeprefix("evidence.")
        upstream_evidence_map[item["evidence_id"]] = sid
        sources.append({
            "record_id": sid, "record_kind": "official_primary_source", "edition": EDITION,
            "status": "candidate", "name": item["title"], "issuer": item["issuer"],
            "url": item["url"], "authority": item["authority"], "source_kind": item["source_kind"],
            "retrieved_on": item["retrieved_on"], "supports": item["supports_surfaces"],
            "use_limit": item["use_limit"], "upstream_ref": item["evidence_id"],
        })

    product_rows, artifact_rows, offer_rows, surface_rows = [], [], [], []
    product_by_key = {}
    for item in PRODUCTS:
        provider_id = "provider.occurrence." + slug(item["provider"])
        providers.setdefault(provider_id, {
            "record_id": provider_id, "record_kind": "provider_organization", "edition": EDITION,
            "status": "candidate", "name": item["provider"], "identity_scope": "legal/project identity only",
            "not_a_capability_class": True, "evidence_posture": "No capability follows from organization identity.",
        })
        pid = "product.occurrence." + item["key"]
        product_by_key[item["key"]] = pid
        evidence_id = "source.occurrence.product." + item["key"]
        sources.append({
            "record_id": evidence_id, "record_kind": "official_primary_source", "edition": EDITION,
            "status": "candidate", "name": item["name"] + " official documentation entry",
            "issuer": item["provider"], "url": item["url"], "authority": "primary",
            "source_kind": "official_product_or_api_documentation", "retrieved_on": AS_OF,
            "supports": ["product identity", "documented candidate surface", "research entry point"],
            "use_limit": "Does not prove a deployment occurrence, entitlement, exact version, numerical limit, conformance, or observed behavior.",
        })
        product_rows.append({
            "record_id": pid, "record_kind": "product_identity", "edition": EDITION, "status": "researched_candidate",
            "name": item["name"], "provider_ref": provider_id, "evidence_refs": [evidence_id],
            "candidate_source_class_refs": item["classes"], "candidate_protocol_refs": item["protocols"],
            "version_scope": item["version"], "deployment_models": item["deployment_models"],
            "identity_laws": ["product != provider", "product != implementation artifact", "product != managed offer", "product != deployment occurrence", "product != connector"],
            "conformance_status": "unproven_until_occurrence_qualification",
        })
        for suffix, artifact_kind in [("release_profile", "implementation_release_profile"), ("qualification_target", "connector_qualification_target")]:
            artifact_rows.append({
                "record_id": f"artifact.occurrence.{item['key']}.{suffix}", "record_kind": "implementation_artifact",
                "edition": EDITION, "status": "candidate", "name": f"{item['name']} {artifact_kind}",
                "product_ref": pid, "artifact_kind": artifact_kind, "version_assertion": item["version"],
                "version_state": "rolling_or_family_requires_occurrence_resolution", "digest": None,
                "source_class_refs": item["classes"], "protocol_refs": item["protocols"], "evidence_refs": [evidence_id],
                "compiler_bindable": False, "refusal_reason": "No exact deployment build, configuration digest, entitlement, or executed qualification receipt.",
            })
        offer_id = "offer.occurrence." + item["key"]
        offer_rows.append({
            "record_id": offer_id, "record_kind": "documented_offer", "edition": EDITION,
            "status": "candidate", "name": item["name"] + " documented offer", "product_ref": pid,
            "offer_kind": item["offer_kind"], "deployment_models": item["deployment_models"],
            "source_class_refs": item["classes"], "protocol_refs": item["protocols"], "evidence_refs": [evidence_id],
            "region": "occurrence_required", "cost": "occurrence_required", "limits": "occurrence_required",
            "support_and_exit": "contract_and_occurrence_required", "compiler_bindable": False,
        })
        for class_id in item["classes"]:
            surface_rows.append({
                "record_id": f"surface.occurrence.{item['key']}.{class_id.rsplit('.',1)[-1]}",
                "record_kind": "product_source_surface", "edition": EDITION, "status": "candidate",
                "name": f"{item['name']} / {class_id}", "product_ref": pid, "offer_ref": offer_id,
                "source_class_ref": class_id, "protocol_refs": item["protocols"], "evidence_refs": [evidence_id],
                "mapping_basis": "official product/API documentation entry plus provider-neutral class interpretation",
                "mapping_confidence": "candidate_not_conformance", "mapping_loss": ["object/profile detail", "tenant entitlement", "exact version", "numerical limits", "observed behavior"],
                "supported_semantics": {
                    "object_discovery": "unknown_until_documented_clause_or_probe",
                    "read": "unknown_until_documented_clause_or_probe",
                    "write": "disabled_until_separately_authorized_and_probed",
                    "change": "unknown_until_documented_clause_or_probe",
                    "schema_change": "source_and_occurrence_specific",
                    "consistency_and_finality": "source_owned_and_occurrence_specific",
                },
            })

    # Requirement and occurrence-template identities are one per provider-neutral class.  When
    # multiple product candidates exist, the first only provides a deterministic research target.
    surfaces_by_class = defaultdict(list)
    for row in surface_rows:
        surfaces_by_class[row["source_class_ref"]].append(row)
    requirements, occurrence_templates, mappings = [], [], []
    source_class_by_id = {row["class_id"]: row for row in source_classes}
    for class_id in sorted(class_ids):
        sc = source_class_by_id[class_id]
        rid = "requirement.occurrence." + class_id.removeprefix("source.")
        requirements.append({
            "record_id": rid, "record_kind": "compiler_requirement", "edition": EDITION, "status": "candidate",
            "name": "Qualified source occurrence for " + sc["name"], "source_class_ref": class_id,
            "required_proofs": ["exact deployment identity", "object and authority scope", "access semantics", "time/order/finality", "security boundary", "limits/cost", "fresh qualification receipts"],
            "material_unknown_policy": "refuse", "write_default": "disabled",
        })
        for index, surface in enumerate(surfaces_by_class[class_id], start=1):
            template_id = f"occurrence-template.occurrence.{surface['product_ref'].removeprefix('product.occurrence.')}.{class_id.rsplit('.',1)[-1]}.{index}"
            occurrence_templates.append({
                "record_id": template_id, "record_kind": "source_occurrence_template", "edition": EDITION,
                "status": "documented_template_not_observed", "name": surface["name"] + " occurrence template",
                "source_class_ref": class_id, "product_ref": surface["product_ref"], "offer_ref": surface["offer_ref"],
                "artifact_ref": "artifact.occurrence." + surface["product_ref"].removeprefix("product.occurrence.") + ".qualification_target",
                "deployment_identity": {"endpoint": "required", "tenant_or_account": "required", "region_or_site": "required", "exact_version_or_build": "required", "configuration_digest": "required"},
                "object_scope": {"objects": "required", "field_authority": "required", "keys": "required", "sensitivity": "required"},
                "access_semantics": surface["supported_semantics"],
                "limits": {name: "required_observed_value_unit_scope_provenance_time_failure_behavior" for name in ["rate", "quota", "page", "payload", "object", "concurrency", "retention", "cursor_ttl", "timeout", "cost_egress"]},
                "security": {"credential_ref": "required_reference_only", "authn": "required", "authz": "required", "network": "required", "encryption": "required", "tenant_boundary": "required", "audit": "required"},
                "freshness": {"observed_at": "required", "expires_at": "required", "invalidation_triggers": ["product release", "API/schema edition", "configuration", "entitlement", "region rollout", "connector build", "security policy", "behavior-change notice"]},
                "probe_receipts": [], "compiler_bindable": False,
            })
            mappings.append({
                "record_id": f"mapping.occurrence.{slug(rid)}.{index}", "record_kind": "requirement_offer_mapping",
                "edition": EDITION, "status": "candidate_unqualified", "name": f"{rid} -> {surface['offer_ref']}",
                "requirement_ref": rid, "offer_ref": surface["offer_ref"], "surface_ref": surface["record_id"],
                "occurrence_template_ref": template_id, "match_kind": "candidate_research_target",
                "binding_phase": "qualification", "compiler_bindable": False,
                "losses": surface["mapping_loss"], "required_receipts": PROBES,
            })

    protocol_crosswalks = []
    for row in protocols:
        protocol_crosswalks.append({
            "record_id": "crosswalk.occurrence." + row["protocol_id"].removeprefix("protocol.cp."),
            "record_kind": "protocol_class_crosswalk", "edition": EDITION, "status": "candidate",
            "name": row["name"] + " class crosswalk", "protocol_ref": row["protocol_id"],
            "source_class_refs": row["source_class_refs"],
            "evidence_refs": [upstream_evidence_map[e] for e in row["evidence_refs"] if e in upstream_evidence_map],
            "preserves": ["protocol/profile identity", "transport/framing declaration", "protocol operation surface"],
            "does_not_establish": ["business semantics", "field authority", "complete schema", "event time", "global order", "finality", "end-to-end exactly once", "deployment limits", "cost", "entitlement"],
            "loss_policy": "each type/schema/time/ordering conversion requires an explicit loss receipt",
        })

    libraries = []
    for i, (key, name) in enumerate(ADAPTER_ROLES, start=1):
        libraries.append({
            "record_id": "library.occurrence." + key, "record_kind": "adapter_library_boundary", "edition": EDITION,
            "status": "candidate", "name": name, "library_role": "pure_or_runtime_adapter_boundary",
            "owns": ["provider-neutral operation interface", "typed configuration", "typed cursor/checkpoint", "typed refusal", "receipt emission", "dependency removal seam"],
            "does_not_own": ["business authority", "source classification", "credentials", "tenant endpoint", "deployment lifecycle", "pipeline orchestration", "sink commit"],
            "decision_points": ["protocol/profile", "discovery", "snapshot", "change/resume", "type mapping", "retry", "backpressure", "limits", "security", "qualification"],
            "composition_ports": ["source_requirement", "occurrence_descriptor", "secret_reference", "network_route", "checkpoint_store", "record_stream", "qualification_receipt", "typed_gap"],
            "write_default": "disabled", "vendor_name_branches": "forbidden",
        })

    semantic_contracts = [{
        "record_id": "library.source.source_cursor",
        "library_id": "library.source.source_cursor",
        "record_kind": "semantic_library_contract",
        "edition": EDITION,
        "status": "specified",
        "name": "Source Cursor Algebra",
        "library_kind": "semantic_pure",
        "effect_boundary": "pure_no_io",
        "semantic_owner_context": "ctx.source.source_cursor",
        "sovereign_question": "Which typed source position delimits acquired source state, and when may two such positions be compared, advanced, translated or used to resume?",
        "positive_scope": [
            "source cursor identity, purpose, issuer, scope, epoch and partition",
            "cursor equality and partial-order comparison",
            "typed advancement, coverage and interval construction",
            "explicit cross-edition or cross-epoch translation with residuals",
            "resume eligibility as a pure predicate over declared evidence",
        ],
        "negative_scope": [
            "cursor acquisition from a live source",
            "checkpoint persistence or acknowledgement",
            "snapshot/change stitching",
            "source finality or completeness",
            "provider token decoding unless a separately bound ACL owns it",
            "retry, polling, scheduling, sink commit or business authority",
        ],
        "public_types": [
            "SourceOccurrenceId", "SourceObjectId", "CursorIssuerId", "CursorPurpose", "SourceCursorParts",
            "SourceEpoch", "SourcePartition", "CursorPayload", "CursorScope",
            "SourceCursor", "CursorOrder", "CursorInterval", "CursorTranslation",
            "CursorResidual", "ResumeEvidence", "ResumeEligibility", "CursorRefusal",
            "CursorComparisonInput", "CursorAdvanceInput", "CursorCoverageInput",
            "CursorIntervalInput", "CursorTranslationInput", "ResumeValidationInput",
        ],
        "public_traits": ["SourceCursorAlgebra", "SourceCursorTranslator"],
        "input_types": ["SourceCursor", "CursorScope", "ResumeEvidence"],
        "output_types": ["CursorOrder", "CursorInterval", "CursorTranslation", "ResumeEligibility"],
        "operation_refs": [
            "operation.source.source_cursor.construct",
            "operation.source.source_cursor.compare",
            "operation.source.source_cursor.advance",
            "operation.source.source_cursor.covers",
            "operation.source.source_cursor.interval",
            "operation.source.source_cursor.translate",
            "operation.source.source_cursor.validate_resume",
        ],
        "operations": [
            {"operation_ref": "operation.source.source_cursor.construct", "input_types": ["SourceCursorParts"], "output_type": "Result<SourceCursor,CursorRefusal>", "purity": "pure"},
            {"operation_ref": "operation.source.source_cursor.compare", "input_types": ["CursorComparisonInput"], "output_type": "Result<CursorOrder,CursorRefusal>", "purity": "pure"},
            {"operation_ref": "operation.source.source_cursor.advance", "input_types": ["CursorAdvanceInput"], "output_type": "Result<SourceCursor,CursorRefusal>", "purity": "pure"},
            {"operation_ref": "operation.source.source_cursor.covers", "input_types": ["CursorCoverageInput"], "output_type": "Result<bool,CursorRefusal>", "purity": "pure"},
            {"operation_ref": "operation.source.source_cursor.interval", "input_types": ["CursorIntervalInput"], "output_type": "Result<CursorInterval,CursorRefusal>", "purity": "pure"},
            {"operation_ref": "operation.source.source_cursor.translate", "input_types": ["CursorTranslationInput"], "output_type": "Result<CursorTranslation,CursorRefusal>", "purity": "pure"},
            {"operation_ref": "operation.source.source_cursor.validate_resume", "input_types": ["ResumeValidationInput"], "output_type": "Result<ResumeEligibility,CursorRefusal>", "purity": "pure"},
        ],
        "decision_refs": [
            "decision.source.source_cursor.carrier_profile",
            "decision.source.source_cursor.purpose",
            "decision.source.source_cursor.scope_granularity",
            "decision.source.source_cursor.comparison_model",
            "decision.source.source_cursor.epoch_transition",
            "decision.source.source_cursor.translation_policy",
            "decision.source.source_cursor.expiry_posture",
            "decision.source.source_cursor.reset_posture",
        ],
        "decisions": [
            {"decision_id": "decision.source.source_cursor.carrier_profile", "question": "Is the native carrier opaque, scalar, tuple, vector, page token or snapshot marker?", "default": None, "default_law": "forbidden"},
            {"decision_id": "decision.source.source_cursor.purpose", "question": "Is this token for paging, incremental query, CDC resume, snapshot cut or replay?", "default": None, "default_law": "forbidden"},
            {"decision_id": "decision.source.source_cursor.scope_granularity", "question": "Which occurrence, object, shard or partition, tenant and authority scope bind comparison?", "default": None, "default_law": "forbidden"},
            {"decision_id": "decision.source.source_cursor.comparison_model", "question": "Is order total, partition-local, partial, equality-only or opaque?", "default": None, "default_law": "forbidden"},
            {"decision_id": "decision.source.source_cursor.epoch_transition", "question": "What happens when source incarnation, topology or history epoch changes?", "default": None, "default_law": "forbidden"},
            {"decision_id": "decision.source.source_cursor.translation_policy", "question": "Which explicit mapper and residual policy may translate editions or epochs?", "default": None, "default_law": "forbidden"},
            {"decision_id": "decision.source.source_cursor.expiry_posture", "question": "How are token expiry and retained source history evidenced?", "default": None, "default_law": "forbidden"},
            {"decision_id": "decision.source.source_cursor.reset_posture", "question": "Which authority may reset, and how is the resulting discontinuity represented?", "default": None, "default_law": "forbidden"},
        ],
        "laws": [
            "A cursor is scoped by issuer, source occurrence, source object, purpose, edition, epoch and partition; differing scope is incomparable unless an explicit translator proves otherwise.",
            "A paging token is not a CDC resume token, a snapshot cut is not a stream offset, and a source cursor is not a durable processing checkpoint.",
            "Opaque payloads admit equality only; arithmetic or lexical ordering is forbidden unless the carrier profile defines it.",
            "Cursor comparison is a partial operation whose incomparable outcome is data, never an exception silently replaced by ordering.",
            "Advance is monotone only inside one declared comparison domain and cannot cross an unresolved gap, expiry, reset or source epoch.",
            "Translation never strengthens order, completeness, finality or replayability and records every loss or ambiguity as a residual.",
            "Reset creates a new epoch or explicit discontinuity; it never masquerades as ordinary advancement.",
            "Observed source position, emitted record, durably stored checkpoint, acknowledged sink effect and source finality remain distinct facts.",
        ],
        "invariants": [
            "every cursor has non-empty issuer, occurrence, object, purpose, edition, epoch, partition and payload identity",
            "equality includes the complete comparison scope and canonical payload identity",
            "an interval has comparable endpoints and cannot reverse the declared order",
            "a successful translation binds input digest, mapper edition, output scope and residual set",
            "resume eligibility cannot be true without unexpired source-history evidence for the exact scope",
        ],
        "error_contracts": [
            "InvalidCursor", "ScopeMismatch", "PurposeMismatch", "EditionMismatch",
            "EpochMismatch", "Incomparable", "Expired", "HistoryUnavailable",
            "GapUnresolved", "TranslationUnavailable", "TranslationLossUnaccepted",
            "ResetNotAuthorized", "ResumeEvidenceMissing", "UnsupportedCapability",
        ],
        "configuration_contracts": ["SourceCursorProfile", "CursorTranslationPolicy", "CursorResetPolicy"],
        "dependencies": [],
        "evidence_refs": ["source.occurrence.product.postgresql", "source.occurrence.product.mongodb", "source.occurrence.product.dataverse"],
        "oracles": [
            "same-scope equality and partial-order laws",
            "cross-scope and cross-purpose negative twins",
            "epoch, reset and expiry state-model fixtures",
            "translation loss monotonicity properties",
            "provider-token ACL differential tests",
        ],
        "gaps": [
            "No provider-token ACL implementation or live occurrence is qualified by this semantic contract.",
            "Two independent law-conformant implementations and executed vertical acceptance remain required for portability.",
        ],
    }]

    innovations = []
    for key, year, name, product_key, compiler_effect in INNOVATIONS:
        innovations.append({
            "record_id": "innovation.occurrence." + key, "record_kind": "innovation_2021_2026", "edition": EDITION,
            "status": "candidate", "name": name, "year": year, "product_ref": product_by_key[product_key],
            "evidence_refs": ["source.occurrence.product." + product_key], "compiler_effect": compiler_effect,
            "ai_or_llm_core": False, "qualification_required": True,
        })

    gaps = [{
        "record_id": "gap.occurrence." + key, "record_kind": "coverage_gap", "edition": EDITION,
        "status": "open", "name": text, "gap_type": key, "materiality": "compiler_binding_or_assurance",
        "closure_evidence": "documented clause plus occurrence-scoped probe/receipt where behavior is mutable",
        "owner": "source occurrence research and qualification program",
    } for key, text in GAPS]

    negative_twins = [{
        "record_id": "negative.occurrence." + key, "record_kind": "negative_twin", "edition": EDITION,
        "status": "active", "name": anti, "invalid_inference": anti, "required_behavior": correct,
        "compiler_response": "typed refusal or explicit unresolved qualification gap",
    } for key, anti, correct in NEGATIVE_TWINS]

    qualification_probes = [{
        "record_id": "probe.occurrence." + name, "record_kind": "qualification_probe", "edition": EDITION,
        "status": "specified_not_executed", "name": name.replace("_", " "), "probe_id": name,
        "scope": "exact endpoint occurrence, object scope, connector build, configuration digest, and time window",
        "allowed_outcomes": ["pass", "fail", "not_supported", "not_authorized", "inconclusive"],
        "empty_result_is_success": False, "requires_live_credentials": True,
        "execution_policy": "not executed by this research corpus; customer-controlled qualification environment only",
    } for name in PROBES]

    manifest_files = {
        "providers.jsonl": list(providers.values()), "products.jsonl": product_rows,
        "implementation-artifacts.jsonl": artifact_rows, "documented-offers.jsonl": offer_rows,
        "product-source-surfaces.jsonl": surface_rows, "occurrence-templates.jsonl": occurrence_templates,
        "compiler-requirements.jsonl": requirements, "requirement-offer-mappings.jsonl": mappings,
        "protocol-class-crosswalks.jsonl": protocol_crosswalks, "adapter-library-boundaries.jsonl": libraries,
        "library-semantic-contracts.jsonl": semantic_contracts,
        "qualification-probes.jsonl": qualification_probes, "official-sources.jsonl": sources,
        "innovations-2021-2026.jsonl": innovations, "negative-twins.jsonl": negative_twins,
        "gaps.jsonl": gaps,
    }
    for name, rows in manifest_files.items():
        dump_jsonl(name, rows)

    unique_urls = {row["url"] for row in sources}
    covered_classes = {row["source_class_ref"] for row in surface_rows}
    used_protocols = {p for row in product_rows for p in row["candidate_protocol_refs"]}
    counts = {name: len(rows) for name, rows in manifest_files.items()}
    combined_identity_records = len(providers) + len(product_rows) + len(artifact_rows)
    payload = {
        "record_id": "manifest.occurrence.catalog.v0_1_0", "record_kind": "manifest", "edition": EDITION,
        "status": "researched_candidate_not_complete", "name": "Source occurrence catalog",
        "as_of": AS_OF, "counts": counts, "combined_provider_product_artifact_records": combined_identity_records,
        "official_primary_source_records": len(sources), "distinct_official_urls": len(unique_urls),
        "source_classes_total": len(class_ids), "source_classes_covered": len(covered_classes),
        "protocol_profiles_total": len(protocol_ids), "protocol_profiles_crosswalked": len(protocol_crosswalks),
        "product_protocol_profiles_used": len(used_protocols),
        "real_live_probes": 0, "credentials_collected": 0,
        "laws": [
            "source capability class != provider organization != product != implementation artifact != documented offer != deployment occurrence != connector",
            "official documentation != conformance receipt != observed behavior",
            "rolling current != exact reproducible version",
            "protocol != data model != business authority",
            "material unknowns refuse binding",
            "write and industrial command surfaces default disabled",
            "no vendor-name branches in compiler semantics",
        ],
        "open_world": True,
        "completion_claim": False,
    }
    payload["files"] = {
        name: {
            "records": len(rows),
            "sha256": hashlib.sha256((ROOT / name).read_bytes()).hexdigest(),
        }
        for name, rows in sorted(manifest_files.items())
    }
    payload["content_digest"] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    (ROOT / "manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
