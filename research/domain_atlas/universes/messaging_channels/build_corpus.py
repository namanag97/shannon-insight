#!/usr/bin/env python3
"""Deterministically build the provider-neutral messaging/channel research corpus."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-26"
EDITION = 1


def source(
    source_id: str,
    title: str,
    organization: str,
    year: int,
    source_kind: str,
    evidence_role: str,
    url: str,
    scope: str,
    canonical: bool,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "title": title,
        "organization": organization,
        "year": year,
        "source_kind": source_kind,
        "evidence_role": evidence_role,
        "url": url,
        "authority_scope": scope,
        "canonical_semantics": canonical,
        "claims_supported": [scope],
        "retrieved_on": AS_OF,
    }


SOURCES = [
    source("src.ietf.rfc9110", "HTTP Semantics", "IETF", 2022, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc9110", "HTTP method, status, representation, and request/response semantics", True),
    source("src.ietf.rfc9112", "HTTP/1.1", "IETF", 2022, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc9112", "HTTP/1.1 framing and connection behavior", True),
    source("src.ietf.rfc9113", "HTTP/2", "IETF", 2022, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc9113", "HTTP/2 streams and flow control", True),
    source("src.ietf.rfc9000", "QUIC: A UDP-Based Multiplexed and Secure Transport", "IETF", 2021, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc9000", "QUIC stream, loss, and connection semantics", True),
    source("src.ietf.rfc9293", "Transmission Control Protocol", "IETF", 2022, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc9293", "TCP ordered byte-stream semantics", True),
    source("src.ietf.rfc6455", "The WebSocket Protocol", "IETF", 2011, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc6455", "WebSocket framing and closure", True),
    source("src.ietf.rfc8446", "The Transport Layer Security Protocol Version 1.3", "IETF", 2018, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc8446", "transport authentication and confidentiality", True),
    source("src.ietf.rfc5321", "Simple Mail Transfer Protocol", "IETF", 2008, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc5321", "SMTP transfer, relay, reply, and mailbox delivery semantics", True),
    source("src.ietf.rfc5322", "Internet Message Format", "IETF", 2008, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc5322", "mail message envelope-content format distinctions", True),
    source("src.ietf.rfc3461", "SMTP Service Extension for Delivery Status Notifications", "IETF", 2003, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc3461", "delivery status notification request semantics", True),
    source("src.ietf.rfc3464", "An Extensible Message Format for Delivery Status Notifications", "IETF", 2003, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc3464", "delivery status evidence envelope", True),
    source("src.ietf.rfc2046", "MIME Part Two: Media Types", "IETF", 1996, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc2046", "multipart content and media-type framing", True),
    source("src.ietf.rfc8259", "The JavaScript Object Notation Data Interchange Format", "IETF", 2017, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc8259", "JSON carrier syntax and interoperability", True),
    source("src.ietf.rfc8949", "Concise Binary Object Representation", "IETF", 2020, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc8949", "CBOR carrier encoding", True),
    source("src.ietf.rfc3339", "Date and Time on the Internet: Timestamps", "IETF", 2002, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc3339", "timestamp representation", True),
    source("src.ietf.rfc3986", "Uniform Resource Identifier: Generic Syntax", "IETF", 2005, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc3986", "endpoint and subject identifier syntax", True),
    source("src.ietf.rfc6585", "Additional HTTP Status Codes", "IETF", 2012, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc6585", "rate-limit refusal status", True),
    source("src.ietf.rfc9218", "Extensible Prioritization Scheme for HTTP", "IETF", 2022, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc9218", "request priority signaling", True),
    source("src.ietf.rfc9331", "RateLimit Header Fields for HTTP", "IETF", 2023, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc9331", "quota and backoff signaling", True),
    source("src.ietf.rfc9421", "HTTP Message Signatures", "IETF", 2024, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc9421", "HTTP message integrity and signer attribution", True),
    source("src.ietf.rfc9457", "Problem Details for HTTP APIs", "IETF", 2023, "standard", "normative_authority", "https://www.rfc-editor.org/rfc/rfc9457", "machine-readable request/refusal details", True),
    source("src.oasis.amqp10", "Advanced Message Queuing Protocol 1.0", "OASIS", 2012, "standard", "normative_authority", "https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-overview-v1.0-os.html", "AMQP nodes, links, transfers, settlement, transactions, and delivery states", True),
    source("src.oasis.amqp10-core", "AMQP Version 1.0 Core Specification", "OASIS", 2012, "standard", "normative_authority", "https://docs.oasis-open.org/amqp/core/v1.0/amqp-core-complete-v1.0.pdf", "complete AMQP 1.0 normative protocol", True),
    source("src.oasis.mqtt5", "MQTT Version 5.0", "OASIS", 2019, "standard", "normative_authority", "https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html", "MQTT sessions, QoS, retained messages, expiry, aliases, and flow control", True),
    source("src.omg.dds14", "Data Distribution Service Version 1.4", "OMG", 2015, "standard", "normative_authority", "https://www.omg.org/spec/DDS/1.4/PDF", "data-centric publish/subscribe and quality-of-service policies", True),
    source("src.omg.rtps25", "Real-time Publish-Subscribe Protocol DDS Interoperability Wire Protocol 2.5", "OMG", 2022, "standard", "normative_authority", "https://www.omg.org/spec/DDSI-RTPS/2.5/PDF", "DDS interoperable wire protocol", True),
    source("src.w3c.trace-context", "Trace Context Level 1", "W3C", 2021, "standard", "normative_authority", "https://www.w3.org/TR/trace-context/", "trace context propagation", True),
    source("src.w3c.websub", "WebSub", "W3C", 2018, "standard", "normative_authority", "https://www.w3.org/TR/websub/", "HTTP publish/subscribe hub protocol", True),
    source("src.w3c.prov-o", "PROV-O: The PROV Ontology", "W3C", 2013, "standard", "normative_authority", "https://www.w3.org/TR/prov-o/", "provenance evidence vocabulary", True),
    source("src.asyncapi.300", "AsyncAPI Specification 3.0.0", "AsyncAPI Initiative", 2023, "specification", "open_specification", "https://www.asyncapi.com/docs/reference/specification/v3.0.0", "channel, operation, message, correlation, and reply description model", True),
    source("src.cloudevents.core", "CloudEvents Specification", "CNCF", 2022, "specification", "open_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md", "protocol-neutral event context and identity", True),
    source("src.cloudevents.primer", "CloudEvents Primer", "CNCF", 2022, "specification", "open_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/primer.md", "separation of event, format, protocol binding, and routing", True),
    source("src.cloudevents.json", "CloudEvents JSON Event Format", "CNCF", 2022, "specification", "open_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/formats/json-format.md", "structured and batch JSON event encoding", True),
    source("src.cloudevents.http", "CloudEvents HTTP Protocol Binding", "CNCF", 2022, "specification", "open_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/bindings/http-protocol-binding.md", "CloudEvents mapping to HTTP", True),
    source("src.cloudevents.amqp", "CloudEvents AMQP Protocol Binding", "CNCF", 2022, "specification", "open_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/bindings/amqp-protocol-binding.md", "CloudEvents mapping to AMQP 1.0", True),
    source("src.cloudevents.kafka", "CloudEvents Kafka Protocol Binding", "CNCF", 2022, "specification", "open_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/bindings/kafka-protocol-binding.md", "CloudEvents mapping to Kafka records", True),
    source("src.cloudevents.mqtt", "CloudEvents MQTT Protocol Binding", "CNCF", 2022, "specification", "open_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/bindings/mqtt-protocol-binding.md", "CloudEvents mapping to MQTT", True),
    source("src.cloudevents.nats", "CloudEvents NATS Protocol Binding", "CNCF", 2022, "specification", "open_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/bindings/nats-protocol-binding.md", "CloudEvents mapping to NATS", True),
    source("src.cloudevents.webhook", "CloudEvents HTTP Webhook", "CNCF", 2022, "specification", "open_specification", "https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/http-webhook.md", "HTTP event delivery handshake and abuse protection", True),
    source("src.cloudevents.subscriptions", "CloudEvents Subscriptions API", "CNCF", 2024, "specification", "open_specification", "https://github.com/cloudevents/spec/blob/main/subscriptions/spec.md", "protocol-neutral subscription management", True),
    source("src.cloudevents.sql", "CloudEvents SQL Expression Language", "CNCF", 2024, "specification", "open_specification", "https://github.com/cloudevents/spec/blob/main/cesql/spec.md", "portable event filtering expressions", True),
    source("src.grpc.core", "gRPC Core Concepts", "gRPC Authors", 2026, "official_oss_docs", "implementation_evidence", "https://grpc.io/docs/what-is-grpc/core-concepts/", "unary and streaming RPC behavior", False),
    source("src.grpc.deadlines", "gRPC Deadlines", "gRPC Authors", 2026, "official_oss_docs", "implementation_evidence", "https://grpc.io/docs/guides/deadlines/", "deadline propagation and expiry", False),
    source("src.grpc.cancellation", "gRPC Cancellation", "gRPC Authors", 2026, "official_oss_docs", "implementation_evidence", "https://grpc.io/docs/guides/cancellation/", "RPC cancellation behavior", False),
    source("src.grpc.retry", "gRPC Retry", "gRPC Authors", 2026, "official_oss_docs", "implementation_evidence", "https://grpc.io/docs/guides/retry/", "transparent and policy-controlled RPC retries", False),
    source("src.grpc.flow", "gRPC Flow Control", "gRPC Authors", 2026, "official_oss_docs", "implementation_evidence", "https://grpc.io/docs/guides/flow-control/", "stream flow control behavior", False),
    source("src.grpc.metadata", "gRPC Metadata", "gRPC Authors", 2026, "official_oss_docs", "implementation_evidence", "https://grpc.io/docs/guides/metadata/", "RPC metadata carriage", False),
    source("src.grpc.status", "gRPC Status Codes", "gRPC Authors", 2026, "official_oss_docs", "implementation_evidence", "https://grpc.io/docs/guides/status-codes/", "RPC outcome taxonomy", False),
    source("src.kafka.design", "Apache Kafka Design", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://kafka.apache.org/documentation/#design", "log, replication, consumer, and delivery implementation semantics", False),
    source("src.kafka.producer", "Kafka Producer Configurations", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://kafka.apache.org/documentation/#producerconfigs", "producer idempotence, batching, retry, and acknowledgement configuration", False),
    source("src.kafka.consumer", "Kafka Consumer Configurations", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://kafka.apache.org/documentation/#consumerconfigs", "consumer groups, offsets, isolation, and fetch controls", False),
    source("src.kafka.broker", "Kafka Broker Configurations", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://kafka.apache.org/documentation/#brokerconfigs", "broker retention, replication, quotas, and transaction configuration", False),
    source("src.kafka.protocol", "Kafka Protocol Guide", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://kafka.apache.org/protocol.html", "Kafka wire request, response, error, and record protocol", False),
    source("src.kafka.kip405", "KIP-405: Kafka Tiered Storage", "Apache Software Foundation", 2023, "official_oss_docs", "implementation_evidence", "https://cwiki.apache.org/confluence/display/KAFKA/KIP-405%3A+Kafka+Tiered+Storage", "tiered log storage design", False),
    source("src.kafka.kip848", "KIP-848: The Next Generation of the Consumer Rebalance Protocol", "Apache Software Foundation", 2024, "official_oss_docs", "implementation_evidence", "https://cwiki.apache.org/confluence/display/KAFKA/KIP-848%3A+The+Next+Generation+of+the+Consumer+Rebalance+Protocol", "broker-driven consumer-group rebalance protocol", False),
    source("src.kafka.kip932", "KIP-932: Queues for Kafka", "Apache Software Foundation", 2024, "official_oss_docs", "implementation_evidence", "https://cwiki.apache.org/confluence/display/KAFKA/KIP-932%3A+Queues+for+Kafka", "share-group queue semantics proposal", False),
    source("src.pulsar.messaging", "Apache Pulsar Messaging", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://pulsar.apache.org/docs/next/concepts-messaging/", "topic, subscription, acknowledgement, redelivery, retention, and routing implementation", False),
    source("src.pulsar.architecture", "Apache Pulsar Architecture", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://pulsar.apache.org/docs/next/concepts-architecture-overview/", "broker and storage separation", False),
    source("src.pulsar.transactions", "Apache Pulsar Transactions", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://pulsar.apache.org/docs/next/txn-why/", "multi-topic transactional publish and acknowledge implementation", False),
    source("src.pulsar.dedup", "Apache Pulsar Message Deduplication", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://pulsar.apache.org/docs/next/cookbooks-deduplication/", "broker-side publication deduplication", False),
    source("src.pulsar.delayed", "Apache Pulsar Delayed Message Delivery", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://pulsar.apache.org/docs/next/concepts-messaging/#delayed-message-delivery", "delayed visibility implementation", False),
    source("src.pulsar.geo", "Apache Pulsar Geo-replication", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://pulsar.apache.org/docs/next/administration-geo/", "cross-cluster replication and replicated subscriptions", False),
    source("src.pulsar.schema", "Apache Pulsar Schema Registry", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://pulsar.apache.org/docs/next/schema-understand/", "schema storage and compatibility enforcement", False),
    source("src.pulsar.compaction", "Apache Pulsar Topic Compaction", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://pulsar.apache.org/docs/next/cookbooks-compaction/", "key-based topic compaction implementation", False),
    source("src.pulsar.tiered", "Apache Pulsar Tiered Storage", "Apache Software Foundation", 2026, "official_oss_docs", "implementation_evidence", "https://pulsar.apache.org/docs/next/tiered-storage-overview/", "offloaded retained log storage", False),
    source("src.nats.core", "NATS Core Concepts", "Synadia Communications", 2026, "official_oss_docs", "implementation_evidence", "https://docs.nats.io/nats-concepts/core-nats", "subjects, publish/subscribe, request/reply, and queue groups", False),
    source("src.nats.subjects", "NATS Subjects", "Synadia Communications", 2026, "official_oss_docs", "implementation_evidence", "https://docs.nats.io/nats-concepts/subjects", "subject naming and wildcard routing", False),
    source("src.nats.queue", "NATS Queue Groups", "Synadia Communications", 2026, "official_oss_docs", "implementation_evidence", "https://docs.nats.io/nats-concepts/core-nats/queue", "load-balanced subscriber groups", False),
    source("src.nats.request", "NATS Request-Reply", "Synadia Communications", 2026, "official_oss_docs", "implementation_evidence", "https://docs.nats.io/nats-concepts/core-nats/reqreply", "inbox-based request/reply", False),
    source("src.nats.jetstream", "JetStream Model Deep Dive", "Synadia Communications", 2026, "official_oss_docs", "implementation_evidence", "https://docs.nats.io/using-nats/developer/develop_jetstream/model_deep_dive", "deduplication, acknowledgement, and exactly-once-feature scope", False),
    source("src.nats.streams", "JetStream Streams", "Synadia Communications", 2026, "official_oss_docs", "implementation_evidence", "https://docs.nats.io/nats-concepts/jetstream/streams", "stream storage, limits, retention, and replication", False),
    source("src.nats.consumers", "JetStream Consumers", "Synadia Communications", 2026, "official_oss_docs", "implementation_evidence", "https://docs.nats.io/nats-concepts/jetstream/consumers", "durable and ephemeral consumer delivery and acknowledgement", False),
    source("src.nats.leafnodes", "NATS Leaf Nodes", "Synadia Communications", 2026, "official_oss_docs", "implementation_evidence", "https://docs.nats.io/running-a-nats-service/configuration/leafnodes", "edge-to-hub federation topology", False),
    source("src.nats.mappings", "NATS Subject Mapping and Partitioning", "Synadia Communications", 2026, "official_oss_docs", "implementation_evidence", "https://docs.nats.io/running-a-nats-service/configuration/subject_mapping", "subject transform and partition routing", False),
    source("src.nats.security", "NATS Security", "Synadia Communications", 2026, "official_oss_docs", "implementation_evidence", "https://docs.nats.io/running-a-nats-service/configuration/securing_nats", "authentication, authorization, and account isolation", False),
    source("src.redis.streams", "Redis Streams", "Redis", 2026, "official_oss_docs", "implementation_evidence", "https://redis.io/docs/latest/develop/data-types/streams/", "append log, groups, pending entries, claiming, and trimming", False),
    source("src.redis.pubsub", "Redis Pub/Sub", "Redis", 2026, "official_oss_docs", "implementation_evidence", "https://redis.io/docs/latest/develop/pubsub/", "ephemeral at-most-once publish/subscribe implementation", False),
    source("src.redis.xack", "Redis XACK", "Redis", 2026, "official_oss_docs", "implementation_evidence", "https://redis.io/docs/latest/commands/xack/", "consumer-group acknowledgement implementation", False),
    source("src.redis.xautoclaim", "Redis XAUTOCLAIM", "Redis", 2026, "official_oss_docs", "implementation_evidence", "https://redis.io/docs/latest/commands/xautoclaim/", "idle pending-entry reassignment", False),
    source("src.redis.xackdel", "Redis XACKDEL", "Redis", 2025, "official_oss_docs", "implementation_evidence", "https://redis.io/docs/latest/commands/xackdel/", "atomic acknowledgement and reference-aware deletion", False),
    source("src.redis.idmp", "Redis Streams Idempotent Message Processing", "Redis", 2026, "official_oss_docs", "implementation_evidence", "https://redis.io/docs/latest/develop/data-types/streams/idempotency/", "producer-identity and sequence based stream deduplication", False),
    source("src.rabbit.confirms", "RabbitMQ Consumer Acknowledgements and Publisher Confirms", "Broadcom", 2026, "official_oss_docs", "implementation_evidence", "https://www.rabbitmq.com/docs/confirms", "publisher-confirm and consumer-acknowledgement scope", False),
    source("src.rabbit.queues", "RabbitMQ Queues", "Broadcom", 2026, "official_oss_docs", "implementation_evidence", "https://www.rabbitmq.com/docs/queues", "queue ordering, durability, and delivery behavior", False),
    source("src.rabbit.quorum", "RabbitMQ Quorum Queues", "Broadcom", 2026, "official_oss_docs", "implementation_evidence", "https://www.rabbitmq.com/docs/quorum-queues", "replicated queue, poison-message, and delivery-limit behavior", False),
    source("src.rabbit.dlx", "RabbitMQ Dead Letter Exchanges", "Broadcom", 2026, "official_oss_docs", "implementation_evidence", "https://www.rabbitmq.com/docs/dlx", "dead-letter routing conditions and safety", False),
    source("src.rabbit.priority", "RabbitMQ Priority Queues", "Broadcom", 2026, "official_oss_docs", "implementation_evidence", "https://www.rabbitmq.com/docs/priority", "priority scheduling implementation", False),
    source("src.rabbit.streams", "RabbitMQ Streams", "Broadcom", 2026, "official_oss_docs", "implementation_evidence", "https://www.rabbitmq.com/docs/streams", "append-only stream and replay implementation", False),
    source("src.rabbit.superstreams", "RabbitMQ Super Streams", "Broadcom", 2026, "official_oss_docs", "implementation_evidence", "https://www.rabbitmq.com/docs/next/streams#super-streams", "partitioned stream abstraction", False),
    source("src.rabbit.federation", "RabbitMQ Federation Plugin", "Broadcom", 2026, "official_oss_docs", "implementation_evidence", "https://www.rabbitmq.com/docs/federation", "broker federation and acknowledgement behavior", False),
    source("src.rabbit.shovel", "RabbitMQ Shovel Plugin", "Broadcom", 2026, "official_oss_docs", "implementation_evidence", "https://www.rabbitmq.com/docs/shovel", "message bridge implementation", False),
    source("src.aws.sqs", "Amazon SQS Developer Guide", "Amazon Web Services", 2026, "provider_documentation", "provider_evidence", "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html", "managed queue offer semantics and limits", False),
    source("src.aws.sns", "Amazon SNS Developer Guide", "Amazon Web Services", 2026, "provider_documentation", "provider_evidence", "https://docs.aws.amazon.com/sns/latest/dg/welcome.html", "managed topic fanout offer semantics and limits", False),
    source("src.aws.kinesis", "Amazon Kinesis Data Streams Developer Guide", "Amazon Web Services", 2026, "provider_documentation", "provider_evidence", "https://docs.aws.amazon.com/streams/latest/dev/introduction.html", "managed partitioned stream offer semantics and limits", False),
    source("src.gcp.pubsub", "Google Cloud Pub/Sub Overview", "Google Cloud", 2026, "provider_documentation", "provider_evidence", "https://cloud.google.com/pubsub/docs/overview", "managed publish/subscribe offer semantics and limits", False),
    source("src.gcp.exactlyonce", "Pub/Sub Exactly-once Delivery", "Google Cloud", 2026, "provider_documentation", "provider_evidence", "https://cloud.google.com/pubsub/docs/exactly-once-delivery", "regional pull-subscription exactly-once feature scope", False),
    source("src.gcp.ordering", "Pub/Sub Order Messages", "Google Cloud", 2026, "provider_documentation", "provider_evidence", "https://cloud.google.com/pubsub/docs/ordering", "ordering-key feature scope", False),
    source("src.azure.servicebus", "Azure Service Bus Messaging Overview", "Microsoft", 2026, "provider_documentation", "provider_evidence", "https://learn.microsoft.com/azure/service-bus-messaging/service-bus-messaging-overview", "managed queues, topics, sessions, transactions, and dead-lettering", False),
    source("src.azure.eventhubs", "Azure Event Hubs Overview", "Microsoft", 2026, "provider_documentation", "provider_evidence", "https://learn.microsoft.com/azure/event-hubs/event-hubs-about", "managed partitioned event-stream offer", False),
    source("src.azure.geo", "Azure Service Bus Geo-replication", "Microsoft", 2025, "provider_documentation", "provider_evidence", "https://learn.microsoft.com/azure/service-bus-messaging/service-bus-geo-replication", "managed metadata and data replication offer", False),
    source("src.paper.lamport", "Time, Clocks, and the Ordering of Events in a Distributed System", "ACM", 1978, "research_paper", "original_research", "https://lamport.azurewebsites.net/pubs/time-clocks.pdf", "happened-before relation and logical clocks", False),
    source("src.paper.snapshot", "Distributed Snapshots: Determining Global States of Distributed Systems", "ACM", 1985, "research_paper", "original_research", "https://lamport.azurewebsites.net/pubs/chandy.pdf", "consistent distributed snapshots", False),
    source("src.paper.endtoend", "End-to-End Arguments in System Design", "ACM", 1984, "research_paper", "original_research", "https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf", "why component guarantees cannot prove application-level correctness", False),
    source("src.paper.twophase", "Notes on Data Base Operating Systems", "Springer", 1978, "research_paper", "original_research", "https://www.cs.cmu.edu/~natassa/courses/15-823/F02/papers/p214-gray.pdf", "transaction, recovery, and two-phase commit foundations", False),
    source("src.paper.sagas", "Sagas", "ACM", 1987, "research_paper", "original_research", "https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf", "long-lived transaction compensation", False),
    source("src.paper.virtualsynchrony", "Exploiting Virtual Synchrony in Distributed Systems", "ACM", 1987, "research_paper", "original_research", "https://www.cs.cornell.edu/projects/Quicksilver/public_pdfs/ExploitingVS.pdf", "group membership and ordered multicast foundations", False),
    source("src.paper.kafka", "Kafka: a Distributed Messaging System for Log Processing", "LinkedIn", 2011, "research_paper", "original_research", "https://cwiki.apache.org/confluence/download/attachments/27822226/Kafka-netdb-06-2011.pdf", "partitioned retained-log design", False),
    source("src.paper.streams", "The Dataflow Model", "Google", 2015, "research_paper", "original_research", "https://research.google/pubs/pub43864/", "event time, processing time, watermarks, and triggers", False),
    source("src.paper.fifo", "Impossibility of Distributed Consensus with One Faulty Process", "ACM", 1985, "research_paper", "original_research", "https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf", "limits of deterministic agreement in asynchronous systems", False),
    source("src.paper.outbox", "Life Beyond Distributed Transactions: an Apostate's Opinion", "Microsoft", 2007, "research_paper", "original_research", "https://www.cidrdb.org/cidr2007/papers/cidr07p15.pdf", "application-level messaging and idempotence without distributed transactions", False),
]


# slug, name, boundary, four typed operation verbs, two domain events, evidence refs, family
CONTEXT_ROWS = [
    ("logical_contract", "Logical Channel Contract", "Owns provider-neutral channel intent, endpoints, message class and semantic constraints.", ["declare", "revise", "validate", "retire"], ["ChannelContractDeclared", "ChannelContractRetired"], ["src.asyncapi.300", "src.cloudevents.primer"], "contract"),
    ("envelope", "Message Envelope", "Owns addressable metadata distinct from application payload and transport frame.", ["compose", "validate", "sign", "unwrap"], ["EnvelopeComposed", "EnvelopeRejected"], ["src.cloudevents.core", "src.ietf.rfc9421"], "contract"),
    ("content", "Message Content", "Owns payload media type, encoding and content negotiation without owning business meaning.", ["encode", "decode", "negotiate", "verify"], ["ContentEncoded", "ContentRejected"], ["src.ietf.rfc2046", "src.ietf.rfc8259", "src.ietf.rfc8949"], "contract"),
    ("command", "Command Channel", "Owns directed requests to an authority to attempt a state-changing action.", ["issue", "authorize", "dispatch", "resolve"], ["CommandIssued", "CommandResolved"], ["src.asyncapi.300", "src.ietf.rfc9110"], "pattern"),
    ("domain_event", "Domain Event Channel", "Owns immutable facts in the publishing domain language after the fact occurred.", ["record", "publish", "subscribe", "supersede"], ["DomainEventRecorded", "DomainEventSuperseded"], ["src.cloudevents.core", "src.paper.lamport"], "pattern"),
    ("integration_event", "Integration Event Channel", "Owns stable published-language facts crossing bounded-context boundaries.", ["project", "version", "publish", "deprecate"], ["IntegrationEventPublished", "IntegrationEventDeprecated"], ["src.cloudevents.core", "src.asyncapi.300"], "pattern"),
    ("data_stream", "Data Stream", "Owns an unbounded sequence contract with explicit progress, update and time semantics.", ["append", "read", "advance_frontier", "close_epoch"], ["StreamElementAppended", "StreamFrontierAdvanced"], ["src.paper.streams", "src.pulsar.messaging"], "pattern"),
    ("retained_log", "Retained Log", "Owns durable ordered records and stable positions for independent readers.", ["append", "fetch_range", "truncate", "seal_segment"], ["LogRecordAppended", "LogSegmentSealed"], ["src.kafka.design", "src.paper.kafka"], "pattern"),
    ("work_queue", "Work Queue", "Owns competing-consumer assignment of work with explicit lease and completion semantics.", ["enqueue", "lease", "complete", "release"], ["WorkEnqueued", "WorkCompleted"], ["src.rabbit.queues", "src.aws.sqs"], "pattern"),
    ("pubsub", "Publish Subscribe", "Owns one-to-many interest-based distribution and subscription isolation.", ["publish", "subscribe", "unsubscribe", "deliver"], ["PublicationAccepted", "SubscriptionChanged"], ["src.oasis.mqtt5", "src.w3c.websub"], "pattern"),
    ("request_reply", "Request Reply", "Owns correlation and bounded response cardinality across asynchronous delivery.", ["request", "correlate", "respond", "expire"], ["RequestSent", "ReplyMatched"], ["src.nats.request", "src.asyncapi.300"], "pattern"),
    ("rpc", "Remote Procedure Call", "Owns remote invocation method, status, deadline, cancellation and streaming shape.", ["invoke", "stream", "cancel", "finish"], ["InvocationStarted", "InvocationFinished"], ["src.grpc.core", "src.grpc.status"], "pattern"),
    ("mailbox", "Mailbox", "Owns durable per-recipient acceptance, retrieval and delivery-status semantics.", ["submit", "accept", "retrieve", "bounce"], ["MessageAcceptedToMailbox", "DeliveryStatusIssued"], ["src.ietf.rfc5321", "src.ietf.rfc3464"], "pattern"),
    ("subscription", "Subscription", "Owns consumer interest, cursor, filter, lease and delivery configuration lifecycle.", ["create", "pause", "resume", "delete"], ["SubscriptionCreated", "SubscriptionPaused"], ["src.cloudevents.subscriptions", "src.pulsar.messaging"], "control"),
    ("consumer_group", "Consumer Group", "Owns cooperative assignment and group progress, not application side effects.", ["join", "assign", "commit_progress", "leave"], ["MemberJoined", "AssignmentsChanged"], ["src.kafka.consumer", "src.redis.streams"], "control"),
    ("partition", "Partition Topology", "Owns finite lanes, partition keys, membership and position domains.", ["create", "select", "split", "merge"], ["PartitionSelected", "PartitionTopologyChanged"], ["src.kafka.design", "src.rabbit.superstreams"], "control"),
    ("routing", "Message Routing", "Owns deterministic address matching, filters, transforms and route decisions.", ["bind", "match", "route", "unbind"], ["RouteBound", "MessageRouted"], ["src.nats.subjects", "src.cloudevents.sql"], "control"),
    ("schema", "Message Schema", "Owns message shape editions, compatibility relation and reader/writer resolution.", ["register", "check_compatibility", "resolve", "deprecate"], ["SchemaRegistered", "SchemaDeprecated"], ["src.pulsar.schema", "src.asyncapi.300"], "contract"),
    ("identity", "Message Identity", "Owns occurrence identity and separates it from business idempotency identity.", ["mint", "validate", "correlate", "rekey"], ["MessageIdentityMinted", "IdentityCollisionDetected"], ["src.cloudevents.core", "src.paper.outbox"], "contract"),
    ("time", "Messaging Time", "Owns event-time, producer-time, broker-time, ingest-time and processing-time labels.", ["stamp", "normalize", "compare", "classify_lateness"], ["TimestampStamped", "LatenessClassified"], ["src.paper.streams", "src.ietf.rfc3339"], "contract"),
    ("ordering", "Ordering Contract", "Owns declared order relation and scope: none, key, partition, causal or total.", ["declare", "sequence", "verify", "detect_gap"], ["SequenceAssigned", "OrderingGapDetected"], ["src.paper.lamport", "src.ietf.rfc9293"], "contract"),
    ("delivery", "Delivery Contract", "Owns per-stage loss/duplication claims and end-to-end proof obligations.", ["declare", "compose", "verify", "downgrade"], ["DeliveryContractDeclared", "DeliveryClaimDowngraded"], ["src.paper.endtoend", "src.oasis.amqp10"], "assurance"),
    ("publication", "Durable Publication", "Owns the boundary from producer intent to durable, addressable broker receipt.", ["prepare", "publish", "confirm", "abort"], ["PublicationPrepared", "PublicationDurablyConfirmed"], ["src.rabbit.confirms", "src.kafka.producer"], "assurance"),
    ("acknowledgement", "Acknowledgement and Settlement", "Owns transport receipt, acceptance, rejection, release and settlement states.", ["ack", "nack", "reject", "settle"], ["DeliveryAcknowledged", "DeliveryRejected"], ["src.oasis.amqp10", "src.rabbit.confirms"], "assurance"),
    ("lease_visibility", "Lease and Visibility", "Owns temporary work ownership and redelivery eligibility after lease expiry.", ["acquire", "extend", "expire", "reassign"], ["DeliveryLeased", "LeaseExpired"], ["src.aws.sqs", "src.redis.xautoclaim"], "assurance"),
    ("retry", "Retry Policy", "Owns new attempts initiated by a caller or policy after a classified failure.", ["classify", "schedule", "attempt", "exhaust"], ["RetryScheduled", "RetryExhausted"], ["src.grpc.retry", "src.ietf.rfc9331"], "recovery"),
    ("redelivery", "Redelivery", "Owns renewed delivery of the same transport occurrence after non-settlement or lease expiry.", ["detect", "redeliver", "count", "stop"], ["RedeliveryStarted", "RedeliveryLimitReached"], ["src.rabbit.quorum", "src.pulsar.messaging"], "recovery"),
    ("delayed_delivery", "Delayed Delivery", "Owns not-before visibility without claiming durable workflow scheduling.", ["schedule", "reschedule", "release_due", "cancel"], ["MessageDelayed", "DelayedMessageReleased"], ["src.pulsar.delayed", "src.oasis.mqtt5"], "recovery"),
    ("deduplication", "Transport Deduplication", "Owns bounded duplicate suppression over message identity and a declared window.", ["remember", "detect", "suppress", "expire_key"], ["DuplicateDetected", "DedupWindowExpired"], ["src.pulsar.dedup", "src.nats.jetstream"], "assurance"),
    ("idempotency", "Business Idempotency", "Owns application effect identity, outcome reuse and conflicting-key refusal.", ["reserve_key", "apply_once", "return_prior", "expire_key"], ["IdempotencyKeyReserved", "PriorOutcomeReturned"], ["src.paper.outbox", "src.ietf.rfc9110"], "assurance"),
    ("transaction", "Messaging Transaction", "Owns atomic visibility boundaries among declared messaging operations only.", ["begin", "enlist", "commit", "abort"], ["MessagingTransactionBegan", "MessagingTransactionCommitted"], ["src.oasis.amqp10-core", "src.pulsar.transactions"], "assurance"),
    ("outbox", "Transactional Outbox", "Owns atomic recording of business mutation and publication intent in one authority.", ["record_intent", "claim", "publish", "mark_published"], ["OutboxIntentRecorded", "OutboxPublicationMarked"], ["src.paper.outbox", "src.paper.twophase"], "recovery"),
    ("inbox", "Transactional Inbox", "Owns durable received identity and atomic application effect or disposition.", ["receive", "reserve", "apply", "record_outcome"], ["InboxItemReserved", "InboxEffectRecorded"], ["src.paper.outbox", "src.paper.endtoend"], "recovery"),
    ("retention", "Retention", "Owns duration/size/legal holds and deletion eligibility for channel records.", ["declare", "evaluate", "hold", "expire"], ["RetentionDeclared", "RecordExpired"], ["src.kafka.broker", "src.nats.streams"], "storage"),
    ("compaction", "Log Compaction", "Owns key-based history reduction and tombstone semantics without claiming full history.", ["select", "compact", "retain_tombstone", "verify"], ["CompactionStarted", "CompactionCompleted"], ["src.pulsar.compaction", "src.kafka.design"], "storage"),
    ("replay", "Replay", "Owns deliberate historical re-consumption from a declared cut under a new attempt identity.", ["select_cut", "authorize", "start", "complete"], ["ReplayAuthorized", "ReplayCompleted"], ["src.rabbit.streams", "src.redis.streams"], "recovery"),
    ("dead_letter", "Dead Letter Routing", "Owns mechanical diversion after a declared terminal delivery condition.", ["classify", "route", "inspect", "redrive"], ["MessageDeadLettered", "DeadLetterRedriven"], ["src.rabbit.dlx", "src.azure.servicebus"], "recovery"),
    ("quarantine", "Quarantine and Adjudication", "Owns isolated custody, investigation, correction authority and release evidence.", ["quarantine", "adjudicate", "correct", "release"], ["MessageQuarantined", "CorrectionAdjudicated"], ["src.w3c.prov-o", "src.ietf.rfc9457"], "governance"),
    ("backpressure", "Backpressure", "Owns demand/capacity signaling and overload response across a channel boundary.", ["measure", "signal", "throttle", "relieve"], ["BackpressureAsserted", "BackpressureRelieved"], ["src.grpc.flow", "src.ietf.rfc9113"], "runtime"),
    ("fanout", "Fanout", "Owns replication of one publication into independently tracked delivery branches.", ["declare", "expand", "deliver_branch", "retire_branch"], ["FanoutExpanded", "BranchDeliveryRecorded"], ["src.aws.sns", "src.w3c.websub"], "pattern"),
    ("priority", "Message Priority", "Owns scheduling preference within an explicitly bounded starvation policy.", ["assign", "compare", "schedule", "age"], ["PriorityAssigned", "PriorityAged"], ["src.rabbit.priority", "src.ietf.rfc9218"], "runtime"),
    ("scheduling", "Message Scheduling", "Owns due-time release and calendar intent beyond short broker delay.", ["schedule", "trigger", "misfire", "cancel"], ["MessageScheduled", "ScheduleMisfired"], ["src.pulsar.delayed", "src.ietf.rfc3339"], "runtime"),
    ("cancellation", "Cancellation", "Owns best-effort stop intent, deadline expiry and terminal cancellation evidence.", ["request", "propagate", "observe", "finalize"], ["CancellationRequested", "CancellationFinalized"], ["src.grpc.cancellation", "src.grpc.deadlines"], "runtime"),
    ("bridge", "Protocol Bridge", "Owns explicit semantic translation between channel/protocol contracts and loss receipts.", ["bind", "translate", "forward", "detach"], ["BridgeBound", "MessageTranslated"], ["src.rabbit.shovel", "src.cloudevents.primer"], "integration"),
    ("federation", "Broker Federation", "Owns cross-domain propagation, loop prevention, topology and failure isolation.", ["link", "replicate", "cutover", "unlink"], ["FederationLinked", "FederationCutover"], ["src.rabbit.federation", "src.nats.leafnodes"], "integration"),
    ("tenancy", "Messaging Tenancy", "Owns tenant namespace, quota, isolation and noisy-neighbor boundaries.", ["provision", "assign_quota", "isolate", "deprovision"], ["TenantProvisioned", "TenantQuotaExceeded"], ["src.nats.security", "src.kafka.broker"], "security"),
    ("security", "Channel Security", "Owns peer identity, authorization, confidentiality, integrity and key posture.", ["authenticate", "authorize", "protect", "revoke"], ["ChannelAuthorized", "ChannelAccessRevoked"], ["src.ietf.rfc8446", "src.ietf.rfc9421"], "security"),
    ("observability", "Messaging Observability", "Owns metrics, traces, logs and lag/age telemetry without owning business truth.", ["instrument", "measure_lag", "trace", "alert"], ["LagMeasured", "DeliveryTraceRecorded"], ["src.w3c.trace-context", "src.redis.streams"], "evidence"),
    ("audit_evidence", "Messaging Evidence", "Owns immutable receipts for declared claims, configurations and observed outcomes.", ["record", "attest", "verify", "retract"], ["MessagingReceiptRecorded", "EvidenceRetracted"], ["src.w3c.prov-o", "src.rabbit.confirms"], "evidence"),
    ("provider_offer", "Provider Capability Offer", "Owns versioned provider claims with scope, limits and qualification hooks.", ["declare", "qualify", "invalidate", "withdraw"], ["ProviderOfferDeclared", "ProviderOfferInvalidated"], ["src.gcp.pubsub", "src.azure.servicebus"], "provider"),
    ("deployed_occurrence", "Deployed Channel Occurrence", "Owns one configured runtime occurrence, endpoints, region, version and receipts.", ["provision", "bind", "observe", "retire"], ["ChannelOccurrenceProvisioned", "ChannelOccurrenceRetired"], ["src.aws.sqs", "src.kafka.broker"], "provider"),
    ("quota", "Messaging Quota", "Owns finite rate, byte, connection and in-flight budgets with explicit refusal behavior.", ["reserve", "consume", "refund", "throttle"], ["QuotaReserved", "QuotaExceeded"], ["src.ietf.rfc9331", "src.kafka.broker"], "runtime"),
    ("bridge_loop", "Bridge Loop Prevention", "Owns hop identity, route history and duplicate-loop refusal across bridges.", ["stamp_hop", "detect_loop", "limit_hops", "drop_with_receipt"], ["BridgeHopStamped", "BridgeLoopDetected"], ["src.rabbit.federation", "src.cloudevents.core"], "integration"),
]


def contexts() -> list[dict[str, Any]]:
    result = []
    for slug, name, boundary, verbs, events, refs, family in CONTEXT_ROWS:
        cid = f"msg.{slug}"
        result.append({
            "context_id": cid,
            "name": name,
            "status": "candidate_not_adjudicated",
            "family": family,
            "domain_vision": f"Make {name.lower()} semantics explicit, composable, testable and provider-neutral.",
            "boundary": boundary,
            "owns": [name.lower(), f"{name.lower()} decisions", f"{name.lower()} receipts"],
            "does_not_own": ["wire protocol implementation", "broker product", "client-library API", "deployed occurrence unless explicitly bound"],
            "ubiquitous_language": list(dict.fromkeys([name.lower(), verbs[0], events[0]])),
            "aggregate_roots": [name.replace(" ", "") + "Contract"],
            "commands": [verb.title().replace("_", "") for verb in verbs],
            "domain_events": events,
            "invariants": [f"Every {name.lower()} assertion names its scope and authority.", "Unknown or unsupported semantics are refused, never inferred from a product label."],
            "refusals": ["REF_UNDECLARED_SEMANTICS", f"REF_{slug.upper()}_PRECONDITION"],
            "lifecycle_summary": "draft -> validated -> active -> retired; every undefined command/state pair refuses deterministically",
            "published_language": [events[0], events[1], "Refusal"],
            "relationships": ["msg.logical_contract", "msg.provider_offer", "msg.deployed_occurrence"] if slug not in {"logical_contract", "provider_offer", "deployed_occurrence"} else ["provider_target", "pipeline_dataflow"],
            "capability_refs": [f"msg.cap.{slug}.contract", f"msg.cap.{slug}.control"],
            "operation_refs": [f"msg.op.{slug}.{verb}" for verb in verbs],
            "decision_ref": f"msg.decision.{slug}",
            "guard_ref": f"msg.guard.{slug}",
            "source_refs": refs,
            "llm_dependency": "none",
        })
    return result


def capabilities() -> list[dict[str, Any]]:
    result = []
    for slug, name, boundary, verbs, _, refs, _ in CONTEXT_ROWS:
        for suffix, label, owned_verbs in (
            ("contract", "contract semantics", verbs[:2]),
            ("control", "runtime control and evidence", verbs[2:]),
        ):
            result.append({
                "capability_id": f"msg.cap.{slug}.{suffix}",
                "owner_context": f"msg.{slug}",
                "name": f"{name} {label}",
                "definition": boundary,
                "operation_refs": [f"msg.op.{slug}.{verb}" for verb in owned_verbs],
                "semantic_level": "provider_neutral",
                "status": "candidate_not_adjudicated",
                "source_refs": refs,
            })
    return result


def operations() -> list[dict[str, Any]]:
    result = []
    for slug, name, boundary, verbs, events, refs, _ in CONTEXT_ROWS:
        for index, verb in enumerate(verbs):
            cap_suffix = "contract" if index < 2 else "control"
            result.append({
                "operation_id": f"msg.op.{slug}.{verb}",
                "owner_context": f"msg.{slug}",
                "capability_ref": f"msg.cap.{slug}.{cap_suffix}",
                "name": f"{verb.replace('_', ' ').title()} {name}",
                "intent": f"Perform {verb.replace('_', ' ')} under the explicit {name.lower()} contract.",
                "signature": {
                    "inputs": [
                        {"name": "contract", "type": f"{name.replace(' ', '')}Contract"},
                        {"name": "request", "type": f"{verb.title().replace('_', '')}Request"},
                    ],
                    "output": {"type": "Outcome", "variants": [events[index % 2], "Refusal", "Failure"]},
                },
                "preconditions": ["contract edition is identified", "authority and tenant are resolved", "resource bounds are declared"],
                "postconditions": ["outcome is terminal and typed", "effects and receipts are correlated", "no stronger delivery claim is synthesized"],
                "invariants": ["message identity is distinct from business idempotency key", "durable receipt is distinct from business acceptance"],
                "refusals": ["REF_UNDECLARED_SEMANTICS", f"REF_{slug.upper()}_PRECONDITION"],
                "effects": ["state_transition", "evidence_receipt"] if verb not in {"validate", "compare", "verify", "inspect", "measure", "detect"} else ["evidence_receipt"],
                "delivery_stage_effects": {"producer_effect": "unproven", "publication": "unproven", "transport": "unproven", "consumption": "unproven", "downstream_effect": "unproven"},
                "determinism": "deterministic_given_contract_state_and_declared_clock",
                "idempotency": "not_assumed; requires explicit business key and retained outcome",
                "information_loss": "none unless a typed loss receipt is emitted",
                "source_refs": refs,
                "status": "candidate_not_adjudicated",
            })
    return result


SPECIAL_DECISIONS = {
    "time": ["event_time", "producer_time", "broker_time", "ingest_time", "processing_time", "multiple_labeled_clocks"],
    "ordering": ["none", "per_key", "per_partition", "causal", "total_with_authority"],
    "delivery": ["best_effort", "at_most_once_stage", "at_least_once_stage", "effectively_once_with_proof", "end_to_end_exactly_once_with_all_stage_proofs"],
    "acknowledgement": ["receipt", "accepted", "rejected", "released", "modified", "business_accepted_separate"],
    "retry": ["none", "bounded_exponential", "server_directed", "budgeted_custom"],
    "redelivery": ["none", "lease_expiry", "negative_ack", "session_recovery", "explicit_requeue"],
    "replay": ["forbidden", "operator_authorized_cut", "consumer_self_service_bounded", "full_history_if_retained"],
    "ordering": ["none", "per_key", "per_partition", "causal", "global_total_with_single_authority"],
    "retention": ["time", "size", "time_and_size", "acknowledged", "legal_hold_overrides"],
    "compaction": ["none", "latest_per_key", "custom_proven_reducer"],
    "dead_letter": ["none", "terminal_failure_route", "delivery_count_route", "expiry_route"],
    "backpressure": ["pull", "credit", "bounded_buffer_block", "throttle", "drop_with_receipt", "fail_fast"],
    "partition": ["none", "hash_key", "range", "round_robin", "explicit_lane"],
    "publication": ["none", "accepted_to_memory", "leader_durable", "quorum_durable", "transaction_committed"],
    "deduplication": ["none", "bounded_time_window", "bounded_sequence_window", "retention_scoped"],
    "idempotency": ["none", "business_key_with_outcome", "natural_key_compare_and_set", "commutative_effect"],
}


def decisions() -> list[dict[str, Any]]:
    result = []
    for slug, name, boundary, verbs, _, refs, _ in CONTEXT_ROWS:
        options = SPECIAL_DECISIONS.get(slug, ["explicit", "forbidden", "provider_bound_after_qualification", "typed_custom"])
        result.append({
            "decision_id": f"msg.decision.{slug}",
            "owner_context": f"msg.{slug}",
            "question": f"Which explicit {name.lower()} policy governs this contract?",
            "decision_plane": "logical" if slug not in {"provider_offer", "deployed_occurrence", "quota"} else "binding",
            "options": options,
            "default_law": "No hidden default: absence is a compile-time gap or typed refusal.",
            "tradeoffs": [boundary, "A stronger local setting may increase cost without strengthening end-to-end effects."],
            "affects_operations": [f"msg.op.{slug}.{verb}" for verb in verbs],
            "source_refs": refs,
            "status": "candidate_not_adjudicated",
        })
    return result


CHANNELS = [
    ("command", "directed_intent", "one", "one", "optional", "authority_defined", "business_result_or_refusal"),
    ("domain_event", "past_fact_inside_domain", "one", "many", "required_for_replay", "declared_scope", "none"),
    ("integration_event", "published_fact_across_domains", "one", "many", "policy", "declared_scope", "none"),
    ("data_stream", "unbounded_observations", "many", "many", "policy", "partition", "none"),
    ("retained_log", "durable_positioned_history", "many", "many", "required", "partition", "none"),
    ("work_queue", "competing_work_assignment", "many", "one_per_group", "required", "queue_or_priority", "completion_or_release"),
    ("ephemeral_pubsub", "online_fanout", "many", "many_online", "none", "none", "none"),
    ("durable_pubsub", "independent_subscription_fanout", "many", "many_groups", "required", "subscription_and_partition", "ack_or_disposition"),
    ("request_reply", "correlated_async_exchange", "one", "one_or_bounded_many", "optional", "correlation", "reply_or_timeout"),
    ("unary_rpc", "one_remote_invocation", "one", "one", "transport_session", "stream", "status_and_response"),
    ("streaming_rpc", "bidirectional_remote_streams", "one", "one", "transport_session", "per_stream", "status_after_stream"),
    ("mailbox", "recipient_addressed_store_and_forward", "many", "one_recipient", "required", "implementation_defined", "delivery_status_optional"),
    ("priority_queue", "preference_scheduled_work", "many", "one_per_group", "required", "priority_then_local", "completion_or_release"),
    ("delayed_queue", "not_before_visible_work", "many", "one_per_group", "required", "due_time_then_local", "completion_or_release"),
    ("compacted_log", "latest_key_state_with_partial_history", "many", "many", "required", "partition", "none"),
    ("dead_letter_channel", "mechanically_diverted_failures", "many", "operator", "required", "arrival_or_source_position", "redrive_disposition"),
    ("quarantine_channel", "adjudication_custody", "many", "authorized_adjudicator", "required", "case_order", "release_or_reject"),
    ("control_channel", "flow_membership_or_lease_control", "many", "protocol_participants", "protocol", "protocol", "control_outcome"),
    ("audit_channel", "evidence_receipts", "many", "auditors", "required", "recording_time_plus_subject", "none"),
    ("bridge_channel", "cross_protocol_translation", "many", "many", "depends_on_both_sides", "minimum_of_scopes", "translation_receipt"),
]


def channel_contracts() -> list[dict[str, Any]]:
    records = []
    context_for = {
        "ephemeral_pubsub": "pubsub", "durable_pubsub": "pubsub", "unary_rpc": "rpc", "streaming_rpc": "rpc",
        "priority_queue": "priority", "delayed_queue": "delayed_delivery", "compacted_log": "compaction",
        "dead_letter_channel": "dead_letter", "quarantine_channel": "quarantine", "control_channel": "backpressure",
        "audit_channel": "audit_evidence", "bridge_channel": "bridge",
    }
    for kind, intent, producers, consumers, durability, ordering, reply in CHANNELS:
        owner = context_for.get(kind, kind)
        records.append({
            "channel_id": f"msg.channel.{kind}",
            "owner_context": f"msg.{owner}",
            "channel_kind": kind,
            "semantic_intent": intent,
            "producer_multiplicity": producers,
            "consumer_multiplicity": consumers,
            "durability": durability,
            "ordering_scope": ordering,
            "reply_shape": reply,
            "delivery_claim_ceiling": "No component-level claim proves end-to-end exactly once; compose all five delivery stages.",
            "required_contract_fields": ["message_class", "address", "schema_edition", "identity", "time_basis", "ordering_scope", "delivery_stages", "retention", "security", "limits"],
            "forbidden_substitutions": ["protocol_for_logical_contract", "broker_for_protocol", "client_for_broker", "offer_for_deployment", "receipt_for_business_acceptance"],
            "status": "candidate_not_adjudicated",
        })
    return records


DISTINCTIONS = [
    ("logical_protocol", "logical channel contract", "wire protocol", "Intent and guarantees survive protocol replacement; framing and handshakes do not."),
    ("protocol_broker", "wire protocol", "broker or engine", "A protocol permits multiple implementations and does not attest a broker configuration."),
    ("broker_client", "broker or engine", "client library", "A client API and retry policy are not the server's persistence or settlement behavior."),
    ("offer_occurrence", "provider capability offer", "deployed occurrence", "A documented offer is not proof that one occurrence enables, preserves, or qualifies it."),
    ("command_event", "command", "event", "A command asks an authority to act; an event asserts a fact already recorded."),
    ("domain_integration", "domain event", "integration event", "Internal language and evolution authority differ from a stable published language."),
    ("message_business_key", "message identity", "business idempotency key", "Occurrence identity detects repeated transport records; the business key scopes effect equivalence."),
    ("partition_global_order", "ordered partition", "global order", "Per-lane order does not compare records in different lanes."),
    ("receipt_acceptance", "durable receipt", "business acceptance", "Persistence or transport settlement does not prove authorization, validation, or domain commit."),
    ("retry_redelivery", "retry", "redelivery", "Retry creates a new attempt; redelivery presents the same transport occurrence again."),
    ("redelivery_replay", "redelivery", "replay", "Redelivery follows unsettled delivery; replay deliberately selects retained history under a new run/attempt."),
    ("dlq_quarantine", "dead-letter channel", "adjudicated quarantine", "DLQ diversion is mechanical; quarantine adds custody, correction authority, evidence, and release decision."),
    ("event_broker_processing_time", "event time", "broker time and processing time", "Occurrence time, broker observation time, and computation time answer different questions."),
    ("ack_effect", "acknowledgement", "downstream effect", "Ack can confirm receipt or settlement while the business side effect is absent, failed, or later compensated."),
]


def semantic_distinctions() -> list[dict[str, Any]]:
    return [{"distinction_id": f"msg.distinction.{slug}", "left": left, "right": right, "non_substitution_law": law, "status": "candidate_not_adjudicated"} for slug, left, right, law in DISTINCTIONS]


def guards() -> list[dict[str, Any]]:
    records = []
    for slug, name, _, _, _, refs, _ in CONTEXT_ROWS:
        records.append({
            "guard_id": f"msg.guard.{slug}",
            "owner_context": f"msg.{slug}",
            "invariants": [
                f"{name} scope, authority and edition are explicit.",
                "Unsupported semantics remain a typed gap.",
                "Evidence is scoped to the layer and occurrence observed.",
            ],
            "refusals": [
                {"code": "REF_UNDECLARED_SEMANTICS", "when": "a required semantic choice is absent", "outcome": "refuse compilation"},
                {"code": f"REF_{slug.upper()}_PRECONDITION", "when": "an operation precondition or resource bound is false", "outcome": "return typed refusal with no hidden fallback"},
            ],
            "source_refs": refs,
            "status": "candidate_not_adjudicated",
        })
    return records


DELIVERY_LAWS = [
    ("stage_separation", "Producer effect, publication, transport, consumption, and downstream effect are five separately proven stages; no stage label implies another."),
    ("exactly_once_non_inference", "Component-level exactly once MUST NOT be used as proof of end-to-end exactly once."),
    ("end_to_end_exactly_once", "End-to-end exactly once requires a single proof covering producer effect identity, atomic publication, loss/duplicate transport behavior, consumer progress, and idempotent or transactional downstream effect."),
    ("weakest_stage_ceiling", "An end-to-end delivery claim cannot exceed the weakest unmitigated stage claim."),
    ("ack_scope", "An acknowledgement proves only its declared settlement scope; durable receipt is not business acceptance."),
    ("confirm_scope", "A publisher confirm proves only the documented broker acceptance/durability scope, not subscriber processing."),
    ("dedup_scope", "Transport deduplication proves suppression only for its identity domain and retention window; it does not prove business idempotency."),
    ("idempotency_scope", "A business idempotency key requires authority, equivalence rule, conflict rule, outcome retention and expiry semantics."),
    ("order_scope", "Per-partition order composes only for records that retain the same partition identity; it never implies global order."),
    ("repartition_order", "Repartitioning terminates the prior lane-order proof unless an explicit resequencing authority emits a new proof."),
    ("retry_identity", "A retry is a new attempt and may create a new message occurrence; correlation does not make it the same delivery."),
    ("redelivery_identity", "A redelivery preserves transport occurrence identity while increasing delivery-attempt evidence."),
    ("replay_identity", "A replay selects historical positions under a new replay/run identity and must not masquerade as redelivery."),
    ("time_non_substitution", "Event time, producer time, broker time, ingest time and processing time are labeled clocks and cannot be substituted without a typed transform."),
    ("dlq_non_correction", "Routing to a DLQ is not adjudication, correction, replay authorization, or proof the message is bad."),
    ("bridge_ceiling", "A bridge may preserve or weaken semantics but cannot strengthen them without new authority and evidence."),
    ("fanout_independence", "One branch's acknowledgement, lag or retention state says nothing about another branch unless a joint contract exists."),
    ("cancellation_race", "Cancellation is a request racing execution; success requires terminal evidence from the effect authority."),
    ("retention_replay", "Replayability is bounded by retained positions, schema readability, keys, authorization, and downstream effect safety."),
    ("transaction_boundary", "A broker transaction is atomic only over documented enlisted resources and cannot include an external business effect by implication."),
]


def delivery_laws() -> list[dict[str, Any]]:
    return [{
        "law_id": f"msg.law.{slug}",
        "statement": statement,
        "proof_obligations": ["scope", "authority", "edition", "configuration", "failure injection", "receipt"],
        "counterexample_required": True,
        "source_refs": ["src.paper.endtoend", "src.oasis.amqp10", "src.rabbit.confirms"],
        "status": "candidate_not_adjudicated",
    } for slug, statement in DELIVERY_LAWS]


LIFECYCLE_ROWS = [
    ("channel_contract", ["draft", "validated", "active", "deprecated", "retired"], "draft", ["retired"], [("validate", "draft", "validated"), ("activate", "validated", "active"), ("deprecate", "active", "deprecated"), ("retire", "deprecated", "retired")]),
    ("message", ["constructed", "publication_pending", "accepted", "available", "leased", "settled", "expired", "dead_lettered", "quarantined"], "constructed", ["settled", "expired", "dead_lettered", "quarantined"], [("publish", "constructed", "publication_pending"), ("confirm", "publication_pending", "accepted"), ("expose", "accepted", "available"), ("lease", "available", "leased"), ("ack", "leased", "settled"), ("lease_expire", "leased", "available"), ("expire", "available", "expired"), ("dead_letter", "available", "dead_lettered"), ("quarantine", "available", "quarantined")]),
    ("subscription", ["requested", "active", "paused", "draining", "deleted", "expired"], "requested", ["deleted", "expired"], [("activate", "requested", "active"), ("pause", "active", "paused"), ("resume", "paused", "active"), ("drain", "active", "draining"), ("delete", "draining", "deleted"), ("expire", "paused", "expired")]),
    ("delivery", ["eligible", "dispatched", "received", "accepted", "rejected", "released", "expired"], "eligible", ["accepted", "rejected", "released", "expired"], [("dispatch", "eligible", "dispatched"), ("receive", "dispatched", "received"), ("accept", "received", "accepted"), ("reject", "received", "rejected"), ("release", "received", "released"), ("expire", "eligible", "expired")]),
    ("consumer_group", ["empty", "forming", "stable", "rebalancing", "closing", "closed"], "empty", ["closed"], [("join", "empty", "forming"), ("assign", "forming", "stable"), ("membership_change", "stable", "rebalancing"), ("reassign", "rebalancing", "stable"), ("close", "stable", "closing"), ("finish", "closing", "closed")]),
    ("transaction", ["idle", "active", "preparing", "committed", "aborted", "in_doubt"], "idle", ["committed", "aborted", "in_doubt"], [("begin", "idle", "active"), ("prepare", "active", "preparing"), ("commit", "preparing", "committed"), ("abort", "active", "aborted"), ("lose_coordinator", "preparing", "in_doubt")]),
    ("outbox_item", ["recorded", "claimed", "published_unconfirmed", "confirmed", "superseded", "quarantined"], "recorded", ["confirmed", "superseded", "quarantined"], [("claim", "recorded", "claimed"), ("publish", "claimed", "published_unconfirmed"), ("confirm", "published_unconfirmed", "confirmed"), ("supersede", "recorded", "superseded"), ("quarantine", "claimed", "quarantined")]),
    ("inbox_item", ["received", "reserved", "effect_applied", "outcome_recorded", "duplicate_returned", "quarantined"], "received", ["outcome_recorded", "duplicate_returned", "quarantined"], [("reserve", "received", "reserved"), ("apply", "reserved", "effect_applied"), ("record", "effect_applied", "outcome_recorded"), ("return_prior", "received", "duplicate_returned"), ("quarantine", "reserved", "quarantined")]),
    ("replay", ["proposed", "authorized", "running", "paused", "completed", "cancelled", "failed"], "proposed", ["completed", "cancelled", "failed"], [("authorize", "proposed", "authorized"), ("start", "authorized", "running"), ("pause", "running", "paused"), ("resume", "paused", "running"), ("complete", "running", "completed"), ("cancel", "running", "cancelled"), ("fail", "running", "failed")]),
    ("quarantine_case", ["open", "investigating", "corrected", "released", "rejected", "expired"], "open", ["released", "rejected", "expired"], [("investigate", "open", "investigating"), ("correct", "investigating", "corrected"), ("release", "corrected", "released"), ("reject", "investigating", "rejected"), ("expire", "open", "expired")]),
    ("provider_offer", ["draft", "documented", "qualified", "degraded", "invalidated", "withdrawn"], "draft", ["invalidated", "withdrawn"], [("document", "draft", "documented"), ("qualify", "documented", "qualified"), ("observe_degradation", "qualified", "degraded"), ("invalidate", "degraded", "invalidated"), ("withdraw", "documented", "withdrawn")]),
    ("deployed_occurrence", ["planned", "provisioned", "bound", "serving", "draining", "retired", "failed"], "planned", ["retired", "failed"], [("provision", "planned", "provisioned"), ("bind", "provisioned", "bound"), ("serve", "bound", "serving"), ("drain", "serving", "draining"), ("retire", "draining", "retired"), ("fail", "serving", "failed")]),
]


def lifecycles() -> list[dict[str, Any]]:
    records = []
    for slug, states, initial, terminal, transitions in LIFECYCLE_ROWS:
        events = sorted({event for event, _, _ in transitions})
        records.append({
            "lifecycle_id": f"msg.lifecycle.{slug}",
            "subject_kind": slug,
            "states": states,
            "events": events,
            "initial_state": initial,
            "terminal_states": terminal,
            "transitions": [{"event": event, "from": start, "to": end} for event, start, end in transitions],
            "undefined_transition": "REF_INVALID_STATE_TRANSITION",
            "totality_law": "For every declared state and event, the listed transition applies or REF_INVALID_STATE_TRANSITION is the terminal typed outcome; no transition is ignored.",
            "status": "candidate_not_adjudicated",
        })
    return records


def requirements() -> list[dict[str, Any]]:
    result = []
    for slug, name, _, _, _, refs, _ in CONTEXT_ROWS:
        result.append({
            "requirement_id": f"msg.requirement.{slug}",
            "owner_context": f"msg.{slug}",
            "intent": f"Require {name.lower()} semantics without selecting an implementation.",
            "required_capabilities": [f"msg.cap.{slug}.contract", f"msg.cap.{slug}.control"],
            "required_decisions": [f"msg.decision.{slug}"],
            "constraints": ["edition pinned", "limits explicit", "failure outcome typed", "evidence retained"],
            "proof_obligations": ["semantic conformance", "failure injection", "observability receipt", "exit test"],
            "source_refs": refs,
            "status": "candidate_not_adjudicated",
        })
    return result


def offers() -> list[dict[str, Any]]:
    result = []
    for slug, name, _, _, _, refs, _ in CONTEXT_ROWS:
        result.append({
            "offer_id": f"msg.offer.{slug}",
            "offer_kind": "versioned_provider_capability_template",
            "satisfies_requirement": f"msg.requirement.{slug}",
            "claimed_capabilities": [f"msg.cap.{slug}.contract", f"msg.cap.{slug}.control"],
            "required_claim_fields": ["provider", "artifact", "version", "region", "configuration", "documented_limits", "failure_domain", "cost", "evidence"],
            "required_receipts": ["conformance", "load", "failure", "recovery", "security", "exit"],
            "claim_ceiling": f"The offer may evidence {name.lower()} support but is not a deployed-occurrence receipt.",
            "source_refs": refs,
            "status": "template_not_provider_claim",
        })
    return result


def compiler_mappings() -> list[dict[str, Any]]:
    result = []
    for slug, _, _, verbs, _, _, _ in CONTEXT_ROWS:
        result.append({
            "mapping_id": f"msg.compiler.{slug}",
            "requirement_ref": f"msg.requirement.{slug}",
            "offer_ref": f"msg.offer.{slug}",
            "logical_input": f"msg.{slug}.contract",
            "checks": ["required decisions resolved", "offer claims qualified", "limits fit workload", "cross-layer loss accepted"],
            "lowering": [f"bind {verb} operation" for verb in verbs],
            "emitted_artifacts": ["logical_channel_contract", "protocol_binding", "provider_binding", "deployment_plan", "qualification_plan"],
            "refusal": "REF_NO_QUALIFIED_MESSAGING_TARGET",
            "status": "candidate_mapping",
        })
    return result


LIBRARIES = [
    ("envelope_kernel", "pure_semantic_kernel", "msg.envelope", "CloudEvents-like envelope validation and projection", "no I/O; cannot publish or attest delivery"),
    ("retained_log_contract", "pure_semantic_kernel", "msg.retained_log", "provider-neutral retained-log identity, position, range, retention and effect-intent algebra", "no I/O; append, fetch, truncate and seal are typed effect intents executed only by a qualified adapter"),
    ("consumer_progress_contract", "pure_semantic_kernel", "msg.consumer_group", "provider-neutral assignment, generation, progress, commit and rebalance algebra", "no I/O; group coordination and progress commits are typed effect intents executed only by a qualified adapter"),
    ("schema_kernel", "pure_semantic_kernel", "msg.schema", "reader/writer compatibility and canonical fingerprints", "no I/O; cannot register remotely or assert runtime compatibility"),
    ("routing_kernel", "pure_semantic_kernel", "msg.routing", "subject matching and filter evaluation", "no I/O; cannot bind broker routes"),
    ("ordering_kernel", "pure_semantic_kernel", "msg.ordering", "sequence and gap validation", "no I/O; cannot create global authority"),
    ("retry_kernel", "pure_semantic_kernel", "msg.retry", "budgeted retry schedule calculation", "no I/O; cannot execute attempts"),
    ("dedup_kernel", "stateful_semantic_library", "msg.deduplication", "bounded identity-window decisions", "state I/O only through supplied store; cannot prove business idempotency"),
    ("idempotency_kernel", "stateful_semantic_library", "msg.idempotency", "business-key reservation and outcome reuse", "state I/O only through an atomic authority; cannot infer key semantics"),
    ("outbox_kernel", "stateful_semantic_library", "msg.outbox", "claim and publication-intent transitions", "database adapter required; cannot promise broker delivery"),
    ("inbox_kernel", "stateful_semantic_library", "msg.inbox", "received-key and effect-outcome transitions", "effect adapter required; cannot infer effect equivalence"),
    ("http_adapter", "protocol_adapter", "msg.request_reply", "map logical request/reply to HTTP", "network I/O allowed; HTTP status is not business acceptance"),
    ("grpc_adapter", "protocol_adapter", "msg.rpc", "map RPC contract to gRPC calls and streams", "network I/O allowed; client retries cannot prove exactly-once effects"),
    ("amqp_adapter", "protocol_adapter", "msg.acknowledgement", "map dispositions and settlement to AMQP 1.0", "network I/O allowed; broker configuration remains external"),
    ("mqtt_adapter", "protocol_adapter", "msg.pubsub", "map topics, sessions and QoS to MQTT 5", "network I/O allowed; QoS 2 is not end-to-end exactly once"),
    ("kafka_adapter", "engine_adapter", "msg.retained_log", "map partitions, offsets and transactions to Kafka", "broker I/O allowed; configuration qualification required"),
    ("pulsar_adapter", "engine_adapter", "msg.subscription", "map topics and subscription modes to Pulsar", "broker I/O allowed; provider-neutral meaning remains upstream"),
    ("nats_adapter", "engine_adapter", "msg.pubsub", "map subjects, queue groups and JetStream consumers", "broker I/O allowed; Core and JetStream semantics must remain distinct"),
    ("redis_stream_adapter", "engine_adapter", "msg.consumer_group", "map pending entries and claims to Redis Streams", "broker I/O allowed; Pub/Sub cannot substitute for Streams"),
    ("rabbit_adapter", "engine_adapter", "msg.work_queue", "map queues, confirms, acks and dead-letter exchanges", "broker I/O allowed; queue type/version must be qualified"),
    ("bridge_runtime", "effectful_bridge", "msg.bridge", "translate between two qualified bindings", "I/O on both sides; must emit semantic-loss and duplicate-risk receipts"),
    ("replay_controller", "effectful_controller", "msg.replay", "authorize and execute bounded historical reads", "I/O allowed; cannot bypass downstream idempotency proof"),
    ("qualification_harness", "test_harness", "msg.provider_offer", "fault, load, conformance and recovery qualification", "test I/O allowed; results scoped to exact occurrence and configuration"),
    ("evidence_recorder", "effectful_evidence_adapter", "msg.audit_evidence", "persist correlated channel receipts", "I/O allowed; observations do not become semantic authority"),
]


EXACT_LIBRARY_CONTRACTS = {
    "envelope_kernel": {
        "public_types": ["EnvelopeId", "EnvelopeSpecVersion", "EventType", "EventSource", "EventSubject", "EventTime", "DataContentType", "DataSchemaRef", "TraceContext", "ExtensionAttribute", "MessageEnvelope", "EnvelopeResidual", "ComposeEnvelopeInput", "ValidateEnvelopeInput", "ProjectEnvelopeInput", "EnvelopeValidation", "EnvelopeProjection", "EnvelopeRefusal"],
        "public_traits": ["MessageEnvelopeAlgebra"],
        "operation_refs": ["operation.msg.envelope.compose", "operation.msg.envelope.validate", "operation.msg.envelope.project"],
        "operations": [
            {"operation_ref": "operation.msg.envelope.compose", "input_types": ["ComposeEnvelopeInput"], "output_type": "Result<MessageEnvelope,EnvelopeRefusal>", "purity": "pure"},
            {"operation_ref": "operation.msg.envelope.validate", "input_types": ["ValidateEnvelopeInput"], "output_type": "Result<EnvelopeValidation,EnvelopeRefusal>", "purity": "pure"},
            {"operation_ref": "operation.msg.envelope.project", "input_types": ["ProjectEnvelopeInput"], "output_type": "Result<EnvelopeProjection,EnvelopeRefusal>", "purity": "pure"},
        ],
        "decision_refs": ["msg.decision.envelope.profile", "msg.decision.envelope.required_attributes", "msg.decision.envelope.extensions", "msg.decision.envelope.time", "msg.decision.envelope.payload_binding", "msg.decision.envelope.projection_loss"],
        "laws": ["Envelope metadata is not payload business meaning.", "Envelope identity is scoped by source and does not imply transport position, ordering or deduplication.", "Event format, protocol binding and transport frame are separate editioned contracts.", "Projection cannot strengthen identity, time, schema, integrity or authority and retains declared residuals.", "A signature or trace context is a bound attribute, not proof that the represented business fact is true."],
        "invariants": ["specification version, id, source and type satisfy the selected envelope profile", "extension names are unique under the selected registry", "payload bytes or reference bind an explicit content and schema posture", "unknown attributes are preserved or refused, never guessed"],
        "error_contracts": ["MissingRequiredAttribute", "InvalidAttribute", "DuplicateExtension", "UnsupportedProfile", "PayloadBindingMismatch", "ProjectionLossUnaccepted", "UnsupportedCapability"],
        "configuration_contracts": ["EnvelopeProfile", "ExtensionRegistry", "EnvelopeProjectionPolicy"],
        "evidence_refs": ["src.cloudevents.core", "src.cloudevents.primer", "src.cloudevents.json"],
        "oracles": ["CloudEvents conformance fixtures", "structured/binary projection round trips", "unknown-extension preservation", "loss-monotonicity properties", "malformed envelope negative twins"],
        "gaps": ["Wire-format and protocol-binding adapters remain separately qualified."],
    },
    "retained_log_contract": {
        "public_types": ["RetainedLogId", "RetainedLogEdition", "LogEpoch", "LogPartition", "LogPosition", "LogRange", "RetentionPolicy", "OrderingScope", "AppendRequirement", "AppendIntent", "FetchRangeIntent", "TruncateIntent", "SealIntent", "LogCapabilityRequirement", "RetainedLogRefusal"],
        "public_traits": ["RetainedLogAlgebra", "RetainedLogEffectPort"],
        "operation_refs": ["operation.msg.retained_log.validate_contract", "operation.msg.retained_log.compare_position", "operation.msg.retained_log.form_append_intent", "operation.msg.retained_log.form_fetch_intent", "operation.msg.retained_log.evaluate_retention"],
        "operations": [
            {"operation_ref": "operation.msg.retained_log.validate_contract", "input_types": ["LogCapabilityRequirement"], "output_type": "Result<RetainedLogEdition,RetainedLogRefusal>", "purity": "pure"},
            {"operation_ref": "operation.msg.retained_log.compare_position", "input_types": ["LogRange"], "output_type": "Result<Ordering,RetainedLogRefusal>", "purity": "pure"},
            {"operation_ref": "operation.msg.retained_log.form_append_intent", "input_types": ["AppendRequirement"], "output_type": "Result<AppendIntent,RetainedLogRefusal>", "purity": "pure", "effect_intent_type": "AppendIntent"},
            {"operation_ref": "operation.msg.retained_log.form_fetch_intent", "input_types": ["LogRange"], "output_type": "Result<FetchRangeIntent,RetainedLogRefusal>", "purity": "pure", "effect_intent_type": "FetchRangeIntent"},
            {"operation_ref": "operation.msg.retained_log.evaluate_retention", "input_types": ["LogRange", "RetentionPolicy"], "output_type": "Result<AvailabilityPosture,RetainedLogRefusal>", "purity": "pure"},
        ],
        "decision_refs": ["msg.decision.retained_log.partitioning", "msg.decision.retained_log.ordering", "msg.decision.retained_log.acknowledgement", "msg.decision.retained_log.retention", "msg.decision.retained_log.compaction", "msg.decision.retained_log.truncation", "msg.decision.retained_log.replay", "msg.decision.retained_log.epoch_transition"],
        "laws": ["A retained log position is scoped by log, edition, epoch and partition and is not a source cursor or consumer checkpoint.", "Per-partition ordering does not imply global or causal ordering.", "Publication acknowledgement, quorum durability, reader visibility and downstream processing completion are distinct facts.", "Retention defines an availability horizon, not a promise that every logical fact remains reconstructable after compaction or deletion.", "Truncation, compaction and tier migration are separate operations with separate information-loss and visibility effects."],
        "invariants": ["positions from different epochs or partitions are incomparable unless an explicit order proof exists", "every append intent binds exact envelope digest, partition decision, acknowledgement requirement and idempotency posture", "every fetch range is finite or budget bounded", "retention and deletion horizons are explicit"],
        "error_contracts": ["LogIdentityMismatch", "EpochMismatch", "PositionIncomparable", "RangeExpired", "OrderingUnsupported", "AcknowledgementUnsupported", "RetentionInsufficient", "CompactionLossUnaccepted", "ResourceExhausted", "UnsupportedCapability"],
        "configuration_contracts": ["RetainedLogContract", "PartitioningPolicy", "RetentionPolicy", "ReplayPolicy"],
        "evidence_refs": ["src.kafka.design", "src.paper.kafka", "src.nats.streams", "src.redis.streams"],
        "oracles": ["position partial-order properties", "epoch and partition negative twins", "retention boundary fixtures", "append/fetch intent conformance", "cross-adapter differential traces"],
        "gaps": ["No broker adapter or deployment is qualified by the pure retained-log contract."],
    },
    "consumer_progress_contract": {
        "public_types": ["ConsumerGroupId", "ConsumerId", "GroupGeneration", "AssignmentEpoch", "PartitionAssignment", "TransportProgress", "ProgressRange", "CommitRequirement", "CommitProgressIntent", "RebalanceInput", "RebalanceOutcome", "ResumeRequirement", "ResumeEligibility", "ConsumerProgressRefusal"],
        "public_traits": ["ConsumerProgressAlgebra", "ConsumerProgressEffectPort"],
        "operation_refs": ["operation.msg.consumer_progress.validate_assignment", "operation.msg.consumer_progress.compare", "operation.msg.consumer_progress.form_commit_intent", "operation.msg.consumer_progress.apply_rebalance", "operation.msg.consumer_progress.validate_resume"],
        "operations": [
            {"operation_ref": "operation.msg.consumer_progress.validate_assignment", "input_types": ["PartitionAssignment"], "output_type": "Result<PartitionAssignment,ConsumerProgressRefusal>", "purity": "pure"},
            {"operation_ref": "operation.msg.consumer_progress.compare", "input_types": ["ProgressRange"], "output_type": "Result<Ordering,ConsumerProgressRefusal>", "purity": "pure"},
            {"operation_ref": "operation.msg.consumer_progress.form_commit_intent", "input_types": ["CommitRequirement"], "output_type": "Result<CommitProgressIntent,ConsumerProgressRefusal>", "purity": "pure", "effect_intent_type": "CommitProgressIntent"},
            {"operation_ref": "operation.msg.consumer_progress.apply_rebalance", "input_types": ["RebalanceInput"], "output_type": "Result<RebalanceOutcome,ConsumerProgressRefusal>", "purity": "pure"},
            {"operation_ref": "operation.msg.consumer_progress.validate_resume", "input_types": ["ResumeRequirement"], "output_type": "Result<ResumeEligibility,ConsumerProgressRefusal>", "purity": "pure"},
        ],
        "decision_refs": ["msg.decision.consumer_progress.assignment", "msg.decision.consumer_progress.commit_boundary", "msg.decision.consumer_progress.rebalance", "msg.decision.consumer_progress.fencing", "msg.decision.consumer_progress.reset", "msg.decision.consumer_progress.retention", "msg.decision.consumer_progress.delivery_posture"],
        "laws": ["Transport progress is not source-native capture position, durable operator checkpoint, handler completion or business-effect completion.", "Progress is scoped by group, log edition, partition, generation and assignment epoch.", "A stale generation or revoked assignment cannot commit progress.", "Committed progress may advance only to the declared acknowledgement boundary and cannot erase an unresolved processing interval.", "Rebalance transfers eligibility, not proof that the prior consumer completed its effects."],
        "invariants": ["each partition has at most one active assignee when the selected model requires exclusivity", "progress is monotone only within one group generation and partition epoch", "commit intent binds assignment fence and acknowledged interval", "reset creates an explicit discontinuity and authority receipt"],
        "error_contracts": ["GroupMismatch", "GenerationStale", "AssignmentRevoked", "ProgressRegression", "ProgressIncomparable", "CommitBeyondAcknowledged", "ProgressExpired", "ResetNotAuthorized", "RebalanceIncomplete", "UnsupportedCapability"],
        "configuration_contracts": ["ConsumerProgressContract", "AssignmentPolicy", "CommitBoundaryPolicy", "ResetPolicy"],
        "evidence_refs": ["src.kafka.consumer", "src.kafka.kip848", "src.nats.consumers", "src.redis.streams"],
        "oracles": ["generation-fencing state model", "monotone progress properties", "rebalance interleaving tests", "commit-boundary negative twins", "cross-adapter differential traces"],
        "gaps": ["No consumer-group adapter or deployment is qualified by the pure progress contract."],
    },
}


def library_boundaries() -> list[dict[str, Any]]:
    rows = []
    for slug, kind, owner, responsibility, effect in LIBRARIES:
        row = {
            "library_id": f"msg.library.{slug}", "library_kind": kind, "semantic_owner_context": owner,
            "candidate_responsibility": responsibility, "effect_boundary": effect, "must_not_own": ["provider-neutral domain meaning outside owner", "undeclared retry", "unscoped exactly-once claim"],
            "qualification_required": kind not in {"pure_semantic_kernel"}, "status": "specified" if slug in EXACT_LIBRARY_CONTRACTS else "candidate_boundary",
        }
        row.update(EXACT_LIBRARY_CONTRACTS.get(slug, {}))
        rows.append(row)
    return rows


IMPLEMENTATION_BOUNDARIES = [
    ("logical", "logical_channel_contract", "msg.logical_contract", "provider-neutral intent, message class and guarantees", "compiles_to"),
    ("logical", "delivery_contract", "msg.delivery", "five-stage delivery proof obligations", "constrains"),
    ("protocol", "amqp_1_0", "msg.acknowledgement", "wire frames, links, transfer and settlement", "may_realize"),
    ("protocol", "mqtt_5", "msg.pubsub", "topic/session/QoS wire behavior", "may_realize"),
    ("protocol", "http_2", "msg.request_reply", "request/response streams and flow control", "may_realize"),
    ("protocol", "grpc_over_http2", "msg.rpc", "RPC mapping, metadata, status, deadlines", "may_realize"),
    ("broker_engine", "apache_kafka", "msg.retained_log", "partitioned replicated log engine", "implements"),
    ("broker_engine", "apache_pulsar", "msg.retained_log", "broker plus segmented storage messaging engine", "implements"),
    ("broker_engine", "nats_jetstream", "msg.retained_log", "NATS persistence and consumer engine", "implements"),
    ("broker_engine", "redis_streams", "msg.retained_log", "Redis append log and group engine", "implements"),
    ("broker_engine", "rabbitmq", "msg.work_queue", "queue, stream and routing engine", "implements"),
    ("client_library", "generic_producer_client", "msg.publication", "serialization, batching and protocol session", "invokes"),
    ("client_library", "generic_consumer_client", "msg.acknowledgement", "fetch/push loop, handler dispatch and ack", "invokes"),
    ("client_library", "generic_rpc_stub", "msg.rpc", "typed method call adapter", "invokes"),
    ("provider_offer", "managed_queue_offer", "msg.provider_offer", "versioned documented service claims and limits", "offers"),
    ("provider_offer", "managed_stream_offer", "msg.provider_offer", "versioned documented service claims and limits", "offers"),
    ("provider_offer", "managed_pubsub_offer", "msg.provider_offer", "versioned documented service claims and limits", "offers"),
    ("deployed_occurrence", "queue_occurrence", "msg.deployed_occurrence", "one configured queue in a region/account/version", "binds"),
    ("deployed_occurrence", "stream_occurrence", "msg.deployed_occurrence", "one configured stream cluster/topic/partition set", "binds"),
    ("deployed_occurrence", "rpc_endpoint_occurrence", "msg.deployed_occurrence", "one deployed service endpoint and policy set", "binds"),
]


def implementation_boundaries() -> list[dict[str, Any]]:
    return [{
        "boundary_id": f"msg.boundary.{kind}.{slug}", "artifact_kind": kind, "name": slug,
        "semantic_owner_context": owner, "owns": owns, "relationship": relation,
        "cannot_prove": ["adjacent-layer conformance", "end-to-end exactly once", "business acceptance without business-authority receipt"],
        "status": "candidate_distinction",
    } for kind, slug, owner, owns, relation in IMPLEMENTATION_BOUNDARIES]


QUALIFICATIONS = [
    ("amqp10_implementation", ["src.oasis.amqp10"], "protocol conformance, settlement and transaction profiles"),
    ("mqtt5_implementation", ["src.oasis.mqtt5"], "session expiry, receive maximum, QoS and retained-message behavior"),
    ("grpc_stack", ["src.grpc.core", "src.grpc.retry"], "deadline, cancellation, retry, status and streaming interoperability"),
    ("apache_kafka", ["src.kafka.design", "src.kafka.producer", "src.kafka.consumer"], "version/configuration-specific log, producer and group behavior"),
    ("apache_pulsar", ["src.pulsar.messaging", "src.pulsar.transactions"], "subscription, storage, deduplication and transaction behavior"),
    ("nats_core", ["src.nats.core"], "ephemeral subject routing and request/reply behavior"),
    ("nats_jetstream", ["src.nats.jetstream", "src.nats.consumers"], "persistence, dedup window, consumer and acknowledgement behavior"),
    ("redis_pubsub", ["src.redis.pubsub"], "ephemeral at-most-once online delivery"),
    ("redis_streams", ["src.redis.streams", "src.redis.xautoclaim"], "retained entries, groups, pending lists, claim and deletion behavior"),
    ("rabbitmq_classic_or_quorum_queue", ["src.rabbit.queues", "src.rabbit.quorum"], "queue-type-specific replication, ordering and poison behavior"),
    ("rabbitmq_stream", ["src.rabbit.streams"], "offset, retention and replay behavior"),
    ("amazon_sqs", ["src.aws.sqs"], "queue-type, region and configuration limits"),
    ("amazon_sns", ["src.aws.sns"], "subscription protocol, filtering and retry policy"),
    ("amazon_kinesis", ["src.aws.kinesis"], "shard, retention, producer and consumer behavior"),
    ("google_cloud_pubsub", ["src.gcp.pubsub", "src.gcp.exactlyonce"], "region, subscription type and exactly-once feature scope"),
    ("azure_service_bus", ["src.azure.servicebus"], "tier, entity, session, duplicate detection and transaction scope"),
    ("azure_event_hubs", ["src.azure.eventhubs"], "partition, retention, protocol and checkpoint behavior"),
]


def provider_qualifications() -> list[dict[str, Any]]:
    return [{
        "qualification_id": f"msg.qualification.{slug}", "target_family": slug,
        "evidence_refs": refs, "scope": scope,
        "required_identity": ["provider", "product_or_project", "version", "deployment_id", "region", "configuration_digest", "client_versions"],
        "required_tests": ["protocol_conformance", "limit_boundary", "partition_failure", "client_disconnect", "redelivery", "retention_expiry", "security_isolation", "upgrade_and_exit"],
        "required_receipts": ["test_plan_digest", "environment_digest", "observations", "counterexamples", "qualified_claims", "expiry_or_invalidation"],
        "forbidden_inferences": ["documentation proves deployed configuration", "component exactly once proves end-to-end exactly once", "marketing tier name proves a semantic contract"],
        "status": "qualification_required_not_executed",
    } for slug, refs, scope in QUALIFICATIONS]


INNOVATIONS = [
    ("kafka_tiered_storage", "2021-2023", "Remote/tiered log segments decouple hot broker disks from long retention.", ["src.kafka.kip405"]),
    ("kafka_consumer_protocol", "2022-2024", "Broker-driven consumer rebalance protocol reduces stop-the-world coordination and centralizes assignments.", ["src.kafka.kip848"]),
    ("kafka_share_groups", "2023-2025", "Share groups add queue-like per-record acquisition and acknowledgement over Kafka topics.", ["src.kafka.kip932"]),
    ("pulsar_transactions", "2021-2022", "Multi-topic transactions coordinate publish and acknowledgement within Pulsar's documented transaction boundary.", ["src.pulsar.transactions"]),
    ("pulsar_replicated_subscriptions", "2021-2024", "Replicated subscription state improves cross-cluster failover continuity.", ["src.pulsar.geo"]),
    ("pulsar_tiered_storage_growth", "2021-2026", "Pluggable offload expands retained-history storage choices.", ["src.pulsar.tiered"]),
    ("nats_jetstream_exactly_once_features", "2021-2022", "Publish deduplication plus double acknowledgement strengthens scoped stream processing guarantees.", ["src.nats.jetstream"]),
    ("nats_leaf_edge_patterns", "2021-2026", "Leaf-node topologies support intermittently connected edge messaging with scoped interest propagation.", ["src.nats.leafnodes"]),
    ("nats_subject_transforms", "2023-2026", "Server-side subject mapping and transforms enable controlled partitioning and namespace adaptation.", ["src.nats.mappings"]),
    ("redis_xautoclaim", "2021", "Automatic claiming scans and reassigns idle pending stream entries.", ["src.redis.xautoclaim"]),
    ("redis_reference_aware_ack_delete", "2025", "XACKDEL coordinates acknowledgement and deletion across stream consumer-group references.", ["src.redis.xackdel"]),
    ("redis_idempotent_stream_production", "2026", "Producer identity and sequencing add bounded duplicate suppression to stream append.", ["src.redis.idmp"]),
    ("rabbitmq_streams", "2021-2022", "An append-only stream protocol adds offset reads and replay alongside queues.", ["src.rabbit.streams"]),
    ("rabbitmq_super_streams", "2022-2024", "Super streams expose a partitioned logical stream over multiple stream queues.", ["src.rabbit.superstreams"]),
    ("rabbitmq_quorum_delivery_limit", "2023-2024", "Quorum-queue delivery limits make poison-message handling explicit.", ["src.rabbit.quorum"]),
    ("cloudevents_subscriptions", "2023-2024", "A protocol-neutral subscription API separates subscription management from native delivery protocols.", ["src.cloudevents.subscriptions"]),
    ("cloudevents_sql", "2023-2024", "A portable expression language standardizes event filtering predicates.", ["src.cloudevents.sql"]),
    ("asyncapi_v3_operation_model", "2023", "AsyncAPI 3 separates operations from channels and adds explicit reply addresses/messages.", ["src.asyncapi.300"]),
    ("http_rate_limit_fields", "2021-2023", "Standard RateLimit fields improve interoperable quota and backoff signaling.", ["src.ietf.rfc9331"]),
    ("http_message_signatures", "2021-2024", "HTTP Message Signatures standardize selective component integrity and signer attribution.", ["src.ietf.rfc9421"]),
    ("http_extensible_priority", "2021-2022", "Urgency and incremental parameters standardize advisory HTTP prioritization.", ["src.ietf.rfc9218"]),
    ("gcp_pubsub_exactly_once", "2022-2026", "Regional pull subscriptions can expose acknowledgement behavior advertised as exactly-once delivery, with documented scope constraints.", ["src.gcp.exactlyonce"]),
    ("azure_service_bus_geo_replication", "2025-2026", "Managed geo-replication adds paired-region entity data replication beyond metadata-only aliasing.", ["src.azure.geo"]),
    ("redis_stream_group_lifecycle", "2025-2026", "Reference-aware trimming and deletion make multi-group lifecycle coordination more explicit.", ["src.redis.streams", "src.redis.xackdel"]),
]


def innovations() -> list[dict[str, Any]]:
    return [{
        "innovation_id": f"msg.innovation.{slug}", "period": period, "summary": summary,
        "why_it_matters": "Candidate change to capability, cost, or operability; it does not alter provider-neutral semantics without adjudication.",
        "evidence_refs": refs, "adoption_posture": "evaluate_and_qualify", "llm_dependency": "none",
        "status": "candidate_not_adjudicated",
    } for slug, period, summary, refs in INNOVATIONS]


GAPS = [
    ("enumeration_saturation", "No independent review proves the 52 context boundaries saturate messaging semantics."),
    ("formal_delivery_calculus", "Delivery-composition laws are prose candidates, not mechanized proofs."),
    ("business_idempotency_expiry", "Cross-domain rules for safe idempotency-key expiry remain application-owned."),
    ("bridge_equivalence", "No general proof decides semantic equivalence across arbitrary protocol bridges."),
    ("causal_order_scaling", "Portable causal-order metadata and truncation policy need further adjudication."),
    ("global_order_authority", "Global ordering under partitions requires an explicit authority and availability trade-off."),
    ("schema_semantics", "Structural compatibility does not establish semantic compatibility."),
    ("quarantine_governance", "Industry-specific correction authorities and legal custody rules remain external."),
    ("mailbox_modernization", "SMTP evidence does not cover every enterprise mailbox/workflow product behavior."),
    ("dds_qualification", "DDS/RTPS provider implementations and QoS interoperability are not qualified here."),
    ("mqtt_session_edges", "Session takeover and shared-subscription failure twins need implementation qualification."),
    ("amqp_transaction_profiles", "Interoperability of optional AMQP transaction capabilities is unqualified."),
    ("grpc_hedging", "Hedged RPC attempts need an application-effect identity proof template."),
    ("priority_fairness", "Portable starvation and fairness bounds across brokers remain unresolved."),
    ("clock_uncertainty", "Broker and producer timestamp uncertainty bounds are not standardized across targets."),
    ("retention_legal_holds", "Legal holds and right-to-erasure conflicts require security/privacy adjudication."),
    ("encrypted_routing", "Payload encryption can defeat filters and routing without a trusted metadata design."),
    ("multi_tenant_side_channels", "Timing, quota and shared-partition side-channel qualification remains deployment-specific."),
    ("cost_model", "Comparable provider-neutral cost functions for ingress, egress, requests, retention and replay remain incomplete."),
    ("energy_model", "Energy evidence for broker, client and retained storage choices is absent."),
    ("upgrade_semantics", "Rolling upgrades may mix protocol/features; portable downgrade proofs remain incomplete."),
    ("disaster_recovery_order", "Cross-region failover ordering and duplicate boundaries require occurrence tests."),
    ("consumer_group_fairness", "Assignment fairness and churn stability are engine-specific and not normalized."),
    ("recurring_freshness", "Official implementation/provider sources need recurring drift checks after the as-of date."),
]


def gaps() -> list[dict[str, Any]]:
    return [{
        "gap_id": f"msg.gap.{slug}", "description": description,
        "blocks_completeness": True, "resolution_evidence": ["primary source", "counterexample", "qualified occurrence receipt", "independent adjudication"],
        "owner_status": "unassigned", "status": "open",
    } for slug, description in GAPS]


def evidence() -> list[dict[str, Any]]:
    return [{
        "evidence_id": f"msg.evidence.{item['source_id'][4:]}", "source_ref": item["source_id"],
        "claim": item["authority_scope"], "evidence_role": item["evidence_role"],
        "canonical_scope": item["canonical_semantics"],
        "defeaters": ["edition drift", "profile mismatch", "configuration mismatch"] + ([] if item["canonical_semantics"] else ["implementation evidence cannot redefine provider-neutral semantics"]),
        "status": "source_indexed_not_independently_reviewed",
    } for item in SOURCES]


EXAMPLES = {
    "examples/commerce-order-command.json": {
        "example_id": "msg.example.commerce_order_command", "vertical": "commerce_order_fulfillment",
        "unrelated_to": "industrial_turbine_telemetry", "channel_contract": "msg.channel.command",
        "message": {"message_id": "msg-7f", "business_idempotency_key": "merchant-9/order-441/place", "event_time": "2026-08-25T09:00:00Z", "broker_time": None, "processing_time": None, "partition_key": "order-441"},
        "delivery_stages": {"producer_effect": "order intent and outbox row atomically recorded", "publication": "quorum receipt required", "transport": "duplicates possible after ambiguous confirm", "consumption": "inbox reservation before handler", "downstream_effect": "payment authorization keyed by order attempt"},
        "acceptance": "Order service emits business acceptance separately from broker acknowledgement.",
        "proof_status": "effectively_once_if_qualified_receipts_hold",
    },
    "examples/commerce-order-command.failure-twin.json": {
        "example_id": "msg.example.commerce_order_command.failure_twin", "vertical": "commerce_order_fulfillment",
        "twin_of": "msg.example.commerce_order_command", "failure": "producer times out after broker commit and retries with a new message_id",
        "unsafe_inference": "broker deduplication by message_id prevents a second payment",
        "actual_risk": "both occurrences pass transport deduplication; only the business idempotency key can collapse the payment effect",
        "required_outcome": "return prior business outcome or refuse conflicting payload under the same key",
    },
    "examples/turbine-telemetry-stream.json": {
        "example_id": "msg.example.turbine_telemetry", "vertical": "industrial_turbine_condition_monitoring",
        "unrelated_to": "commerce_order_fulfillment", "channel_contract": "msg.channel.data_stream",
        "message": {"message_id": "sensor-22/boot-3/seq-81", "business_idempotency_key": None, "event_time": "2026-08-25T08:59:58Z", "broker_time": "2026-08-25T09:00:04Z", "processing_time": "2026-08-25T09:00:07Z", "partition_key": "turbine-22"},
        "ordering": "per turbine partition only", "retention": "14 days hot plus qualified tiered history", "late_data": "update condition window within allowed lateness; quarantine impossible clock regressions",
        "proof_status": "at_least_once_transport_with_idempotent_window_state",
    },
    "examples/turbine-telemetry-stream.failure-twin.json": {
        "example_id": "msg.example.turbine_telemetry.failure_twin", "vertical": "industrial_turbine_condition_monitoring",
        "twin_of": "msg.example.turbine_telemetry", "failure": "bridge repartitions by site and stamps bridge time as event time",
        "unsafe_inference": "each output partition is ordered, so turbine observations and event-time windows remain correct",
        "actual_risk": "repartition ends the source order proof and broker time cannot replace sensor event time; alerts can be suppressed or duplicated",
        "required_outcome": "preserve source identity/time, emit translation-loss receipt, and resequence only under an explicit turbine authority",
    },
}


def schema(title: str, required: list[str], properties: dict[str, Any]) -> dict[str, Any]:
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": title, "type": "object", "required": required, "properties": properties, "additionalProperties": False}


S = {"type": "string", "minLength": 1}
SA = {"type": "array", "items": S, "minItems": 1, "uniqueItems": True}
OBJ = {"type": "object", "minProperties": 1}
BOOL = {"type": "boolean"}


def schemas() -> dict[str, dict[str, Any]]:
    defs: dict[str, tuple[list[str], dict[str, Any]]] = {
        "source": (["source_id", "title", "organization", "year", "source_kind", "evidence_role", "url", "authority_scope", "canonical_semantics", "claims_supported", "retrieved_on"], {"source_id": S, "title": S, "organization": S, "year": {"type": "integer"}, "source_kind": S, "evidence_role": S, "url": {"type": "string", "pattern": "^https://"}, "authority_scope": S, "canonical_semantics": BOOL, "claims_supported": SA, "retrieved_on": S}),
        "bounded-context": (["context_id", "name", "status", "family", "domain_vision", "boundary", "owns", "does_not_own", "ubiquitous_language", "aggregate_roots", "commands", "domain_events", "invariants", "refusals", "lifecycle_summary", "published_language", "relationships", "capability_refs", "operation_refs", "decision_ref", "guard_ref", "source_refs", "llm_dependency"], {"context_id": S, "name": S, "status": S, "family": S, "domain_vision": S, "boundary": S, "owns": SA, "does_not_own": SA, "ubiquitous_language": SA, "aggregate_roots": SA, "commands": SA, "domain_events": SA, "invariants": SA, "refusals": SA, "lifecycle_summary": S, "published_language": SA, "relationships": SA, "capability_refs": SA, "operation_refs": SA, "decision_ref": S, "guard_ref": S, "source_refs": SA, "llm_dependency": {"const": "none"}}),
        "capability": (["capability_id", "owner_context", "name", "definition", "operation_refs", "semantic_level", "status", "source_refs"], {"capability_id": S, "owner_context": S, "name": S, "definition": S, "operation_refs": SA, "semantic_level": S, "status": S, "source_refs": SA}),
        "operation": (["operation_id", "owner_context", "capability_ref", "name", "intent", "signature", "preconditions", "postconditions", "invariants", "refusals", "effects", "delivery_stage_effects", "determinism", "idempotency", "information_loss", "source_refs", "status"], {"operation_id": S, "owner_context": S, "capability_ref": S, "name": S, "intent": S, "signature": OBJ, "preconditions": SA, "postconditions": SA, "invariants": SA, "refusals": SA, "effects": SA, "delivery_stage_effects": OBJ, "determinism": S, "idempotency": S, "information_loss": S, "source_refs": SA, "status": S}),
        "decision": (["decision_id", "owner_context", "question", "decision_plane", "options", "default_law", "tradeoffs", "affects_operations", "source_refs", "status"], {"decision_id": S, "owner_context": S, "question": S, "decision_plane": S, "options": SA, "default_law": S, "tradeoffs": SA, "affects_operations": SA, "source_refs": SA, "status": S}),
        "channel-contract": (["channel_id", "owner_context", "channel_kind", "semantic_intent", "producer_multiplicity", "consumer_multiplicity", "durability", "ordering_scope", "reply_shape", "delivery_claim_ceiling", "required_contract_fields", "forbidden_substitutions", "status"], {"channel_id": S, "owner_context": S, "channel_kind": S, "semantic_intent": S, "producer_multiplicity": S, "consumer_multiplicity": S, "durability": S, "ordering_scope": S, "reply_shape": S, "delivery_claim_ceiling": S, "required_contract_fields": SA, "forbidden_substitutions": SA, "status": S}),
        "semantic-distinction": (["distinction_id", "left", "right", "non_substitution_law", "status"], {"distinction_id": S, "left": S, "right": S, "non_substitution_law": S, "status": S}),
        "guard": (["guard_id", "owner_context", "invariants", "refusals", "source_refs", "status"], {"guard_id": S, "owner_context": S, "invariants": SA, "refusals": {"type": "array", "items": OBJ, "minItems": 1}, "source_refs": SA, "status": S}),
        "delivery-law": (["law_id", "statement", "proof_obligations", "counterexample_required", "source_refs", "status"], {"law_id": S, "statement": S, "proof_obligations": SA, "counterexample_required": BOOL, "source_refs": SA, "status": S}),
        "lifecycle": (["lifecycle_id", "subject_kind", "states", "events", "initial_state", "terminal_states", "transitions", "undefined_transition", "totality_law", "status"], {"lifecycle_id": S, "subject_kind": S, "states": SA, "events": SA, "initial_state": S, "terminal_states": SA, "transitions": {"type": "array", "items": OBJ, "minItems": 1}, "undefined_transition": S, "totality_law": S, "status": S}),
        "requirement": (["requirement_id", "owner_context", "intent", "required_capabilities", "required_decisions", "constraints", "proof_obligations", "source_refs", "status"], {"requirement_id": S, "owner_context": S, "intent": S, "required_capabilities": SA, "required_decisions": SA, "constraints": SA, "proof_obligations": SA, "source_refs": SA, "status": S}),
        "offer": (["offer_id", "offer_kind", "satisfies_requirement", "claimed_capabilities", "required_claim_fields", "required_receipts", "claim_ceiling", "source_refs", "status"], {"offer_id": S, "offer_kind": S, "satisfies_requirement": S, "claimed_capabilities": SA, "required_claim_fields": SA, "required_receipts": SA, "claim_ceiling": S, "source_refs": SA, "status": S}),
        "compiler-mapping": (["mapping_id", "requirement_ref", "offer_ref", "logical_input", "checks", "lowering", "emitted_artifacts", "refusal", "status"], {"mapping_id": S, "requirement_ref": S, "offer_ref": S, "logical_input": S, "checks": SA, "lowering": SA, "emitted_artifacts": SA, "refusal": S, "status": S}),
        "library-boundary": (["library_id", "library_kind", "semantic_owner_context", "candidate_responsibility", "effect_boundary", "must_not_own", "qualification_required", "status"], {"library_id": S, "library_kind": S, "semantic_owner_context": S, "candidate_responsibility": S, "effect_boundary": S, "must_not_own": SA, "qualification_required": BOOL, "status": S, "public_types": SA, "public_traits": SA, "operation_refs": SA, "operations": {"type": "array", "items": OBJ, "minItems": 1}, "decision_refs": SA, "laws": SA, "invariants": SA, "error_contracts": SA, "configuration_contracts": SA, "dependencies": {"type": "array", "items": S, "uniqueItems": True}, "evidence_refs": SA, "oracles": SA, "gaps": SA}),
        "implementation-boundary": (["boundary_id", "artifact_kind", "name", "semantic_owner_context", "owns", "relationship", "cannot_prove", "status"], {"boundary_id": S, "artifact_kind": S, "name": S, "semantic_owner_context": S, "owns": S, "relationship": S, "cannot_prove": SA, "status": S}),
        "provider-qualification": (["qualification_id", "target_family", "evidence_refs", "scope", "required_identity", "required_tests", "required_receipts", "forbidden_inferences", "status"], {"qualification_id": S, "target_family": S, "evidence_refs": SA, "scope": S, "required_identity": SA, "required_tests": SA, "required_receipts": SA, "forbidden_inferences": SA, "status": S}),
        "innovation": (["innovation_id", "period", "summary", "why_it_matters", "evidence_refs", "adoption_posture", "llm_dependency", "status"], {"innovation_id": S, "period": {"type": "string", "pattern": "202[1-6]"}, "summary": S, "why_it_matters": S, "evidence_refs": SA, "adoption_posture": S, "llm_dependency": {"const": "none"}, "status": S}),
        "evidence": (["evidence_id", "source_ref", "claim", "evidence_role", "canonical_scope", "defeaters", "status"], {"evidence_id": S, "source_ref": S, "claim": S, "evidence_role": S, "canonical_scope": BOOL, "defeaters": SA, "status": S}),
        "gap": (["gap_id", "description", "blocks_completeness", "resolution_evidence", "owner_status", "status"], {"gap_id": S, "description": S, "blocks_completeness": BOOL, "resolution_evidence": SA, "owner_status": S, "status": S}),
    }
    return {name: schema(f"Messaging {name}", required, props) for name, (required, props) in defs.items()}


REGISTRIES = {
    "sources.jsonl": ("source", SOURCES, "source_id"),
    "bounded-context-candidates.jsonl": ("bounded-context", contexts(), "context_id"),
    "capabilities.jsonl": ("capability", capabilities(), "capability_id"),
    "typed-operations.jsonl": ("operation", operations(), "operation_id"),
    "decision-points.jsonl": ("decision", decisions(), "decision_id"),
    "channel-contracts.jsonl": ("channel-contract", channel_contracts(), "channel_id"),
    "semantic-distinctions.jsonl": ("semantic-distinction", semantic_distinctions(), "distinction_id"),
    "invariants-refusals.jsonl": ("guard", guards(), "guard_id"),
    "delivery-composition-laws.jsonl": ("delivery-law", delivery_laws(), "law_id"),
    "lifecycles.jsonl": ("lifecycle", lifecycles(), "lifecycle_id"),
    "compiler-requirements.jsonl": ("requirement", requirements(), "requirement_id"),
    "capability-offers.jsonl": ("offer", offers(), "offer_id"),
    "compiler-mappings.jsonl": ("compiler-mapping", compiler_mappings(), "mapping_id"),
    "library-adapter-boundaries.jsonl": ("library-boundary", library_boundaries(), "library_id"),
    "implementation-boundaries.jsonl": ("implementation-boundary", implementation_boundaries(), "boundary_id"),
    "provider-qualification-requirements.jsonl": ("provider-qualification", provider_qualifications(), "qualification_id"),
    "innovations.jsonl": ("innovation", innovations(), "innovation_id"),
    "evidence.jsonl": ("evidence", evidence(), "evidence_id"),
    "gaps.jsonl": ("gap", gaps(), "gap_id"),
}


def jsonl(records: list[dict[str, Any]], key: str) -> str:
    return "".join(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n" for record in sorted(records, key=lambda item: item[key]))


def counts() -> dict[str, int]:
    return {
        "sources": len(SOURCES), "bounded_context_candidates": len(contexts()), "capabilities": len(capabilities()),
        "typed_operations": len(operations()), "decision_points": len(decisions()), "channel_contracts": len(channel_contracts()),
        "capability_operation_decision_channel_records": len(capabilities()) + len(operations()) + len(decisions()) + len(channel_contracts()),
        "semantic_distinctions": len(semantic_distinctions()), "invariants_refusals": len(guards()),
        "delivery_composition_laws": len(delivery_laws()), "lifecycles": len(lifecycles()),
        "compiler_requirements": len(requirements()), "capability_offers": len(offers()), "compiler_mappings": len(compiler_mappings()),
        "library_adapter_boundaries": len(library_boundaries()), "implementation_boundaries": len(implementation_boundaries()),
        "provider_qualification_requirements": len(provider_qualifications()), "innovations": len(innovations()),
        "evidence_records": len(evidence()), "gaps": len(gaps()), "vertical_examples": 2, "failure_twins": 2,
    }


def manifest() -> dict[str, Any]:
    return {
        "universe_id": "messaging_channels", "edition": EDITION, "as_of": AS_OF,
        "status": "researched_candidate_not_adjudicated", "completion_claim": False,
        "unit": "provider-neutral logical messaging/channel contract with explicit delivery, time, ordering, recovery and evidence semantics",
        "not_units": ["wire protocol", "broker or engine", "client library", "provider offer", "deployed occurrence"],
        "counts": counts(),
        "delivery_stages": ["producer_effect", "publication", "transport", "consumption", "downstream_effect"],
        "artifact_layers": ["logical", "protocol", "broker_engine", "client_library", "provider_offer", "deployed_occurrence"],
        "forbidden_claims": ["component exactly once proves end-to-end exactly once", "durable receipt proves business acceptance", "ordered partition proves global order", "DLQ placement proves adjudicated correction"],
        "forbidden_core_dependencies": ["llm", "large_language_model", "generative_model", "prompt", "rag", "agent_memory"],
        "standing": "broad primary-source-backed candidate corpus; independent adjudication, provider occurrence qualification, recurring freshness and saturation remain open",
    }


def coverage_report() -> dict[str, Any]:
    return {
        "report_id": "msg.coverage.edition1", "as_of": AS_OF, "counts": counts(),
        "source_evidence_roles": dict(sorted(Counter(item["evidence_role"] for item in SOURCES).items())),
        "source_organizations": len({item["organization"] for item in SOURCES}),
        "families": dict(sorted(Counter(row[6] for row in CONTEXT_ROWS).items())),
        "critical_distinctions": [item[0] for item in DISTINCTIONS],
        "delivery_stage_coverage": ["producer_effect", "publication", "transport", "consumption", "downstream_effect"],
        "validation_posture": "structural, referential, semantic sentinel, deterministic regeneration and failure-twin checks",
        "completion_claim": False, "open_gap_count": len(GAPS), "independent_review": "not_performed",
    }


def readme() -> str:
    c = counts()
    return f"""# Messaging and channel universe

Status: evidence-backed research candidate; not adjudicated and not a completeness claim.

The semantic unit is a provider-neutral logical messaging/channel contract. Protocols, engines,
libraries, offers, and deployments are related evidence-bearing artifacts, never synonyms.

```text
business intent / facts / observations
                 |
                 v
       logical channel contract
       (identity, time, order, delivery, retention, security)
                 |
          compiler requirement
                 v
          protocol binding  <----> client / adapter boundary
                 |
                 v
          broker or engine  <----> versioned provider offer
                 |
                 v
       deployed occurrence (configuration + limits + receipts)
                 |
                 v
  producer effect -> publication -> transport -> consumption -> downstream effect
       proof              proof          proof          proof              proof
```

No component-level `exactly once` feature proves end-to-end exactly once. The five stages above
must be established separately and composed. A broker acknowledgement can be durable receipt but
is not business acceptance. A message identifier is not a business idempotency key. Per-partition
order is not global order. Retry, redelivery and replay have different attempt identities. A DLQ is
mechanical diversion; adjudicated quarantine owns custody, correction and release.

Time is labeled: event time, producer time, broker time, ingest time and processing time cannot be
substituted silently. Bridges can preserve or weaken a contract and must receipt any loss; they
cannot strengthen semantics merely by choosing a more capable target.

## Corpus

- {c['sources']} primary/official sources, with implementation and provider documentation scoped as evidence rather than canonical domain semantics.
- {c['bounded_context_candidates']} bounded-context candidates.
- {c['capabilities']} capabilities, {c['typed_operations']} typed operations, {c['decision_points']} decisions and {c['channel_contracts']} channel contracts ({c['capability_operation_decision_channel_records']} combined records).
- {c['lifecycles']} total lifecycles, {c['delivery_composition_laws']} delivery-composition laws and {c['invariants_refusals']} invariant/refusal records.
- {c['compiler_requirements']} requirements, {c['capability_offers']} offer templates and {c['compiler_mappings']} compiler mappings.
- {c['library_adapter_boundaries']} library/adapter boundaries, {c['implementation_boundaries']} layer-boundary records and {c['provider_qualification_requirements']} qualification profiles.
- {c['innovations']} non-generative 2021-2026 innovation candidates, {c['evidence_records']} evidence records and {c['gaps']} honest gaps.
- Two unrelated verticals—commerce order commands and industrial turbine telemetry—with a failure twin for each.

## Files and validation

All registries are deterministic JSONL and each has a JSON Schema in `schemas/`. Example artifacts
are under `examples/`. `manifest.json` and `coverage-report.json` state exact counts and candidate
status. Regenerate with `python3 build_corpus.py`; verify with `python3 validate_corpus.py`.

The validator checks deterministic regeneration, schemas, unique IDs, references, layer separation,
source authority, lifecycle totality, delivery-stage non-inference laws, innovations, vertical
independence, failure twins, LLM/generative exclusion, counts, and honest incompleteness.
"""


def render() -> dict[Path, str]:
    output: dict[Path, str] = {}
    for filename, (_, records, key) in REGISTRIES.items():
        output[ROOT / filename] = jsonl(records, key)
    for name, value in schemas().items():
        output[ROOT / "schemas" / f"{name}.schema.json"] = json.dumps(value, indent=2, sort_keys=True) + "\n"
    for filename, value in EXAMPLES.items():
        output[ROOT / filename] = json.dumps(value, indent=2, sort_keys=True) + "\n"
    output[ROOT / "manifest.json"] = json.dumps(manifest(), indent=2, sort_keys=True) + "\n"
    output[ROOT / "coverage-report.json"] = json.dumps(coverage_report(), indent=2, sort_keys=True) + "\n"
    output[ROOT / "README.md"] = readme()
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files differ")
    args = parser.parse_args()
    rendered = render()
    drift = []
    for path, content in sorted(rendered.items()):
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                drift.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if drift:
        print("DRIFT: " + ", ".join(drift))
        return 1
    print(json.dumps({"status": "clean" if args.check else "written", "counts": counts()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
