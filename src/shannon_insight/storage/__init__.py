"""Parquet-based storage layer for the tensor DB migration.

Writes event data to Parquet files and reads them back. Runs alongside
the existing SQLite persistence layer during the strangler-fig migration.
"""
