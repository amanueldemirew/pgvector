# RAG AI Agent

A RAG-based AI agent for task tracking and management using LlamaIndex and Google's Gemini models.

## Description

This project implements a Retrieval-Augmented Generation (RAG) AI agent that helps with task tracking and management. It uses LlamaIndex for vector storage and retrieval, and Google's Gemini models for embeddings.

## Requirements

- Python 3.11
- PostgreSQL database
- Google Cloud API credentials for Gemini

## Dependencies

- llama-index >= 0.9.0
- llama-index-embeddings-gemini
- llama-index-llms-gemini 
- llama-index-readers-database
- llama-index-vector-stores-postgres
- python-dotenv >= 1.0.0
- sqlalchemy >= 2.0.0
- psycopg2-binary >= 2.9.0
- pydantic-ai >= 0.0.29, < 0.0.30

## Installation

1. Clone the repository
2. Install dependencies using Poetry:
