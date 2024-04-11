
# Research Assistant AI
The Research Assistant AI application is designed to provide users with an interactive platform to ask research-related questions and receive responses from an AI-powered research agent. The project includes a command-line interface (CLI), a WebSocket-based API, and a user-friendly web interface built with Streamlit.

---
![Alt text](/imgs/webapp.png "Web Interface")

## Research Agent and Tools

The main part of application is built from the Research Agent, an AI-powered (OpenAI) system designed to assist users with their research inquiries. The agent, built using LangChain, leverages the capabilities of the following tools:

-  **Arxiv Retrival**: Users can query for Arxiv research papers based on paper name, topic, authors, etc.
  
-  **BibTex Generation**: Users can ask for the BibTex of the queried papers.

The Research Agent processes user input, generates responses, and maintains a chat history to provide a great conversational experience.


## API Server (FastAPI)

The API server, built using FastAPI, serves as the backend for handling user requests, managing WebSocket connections, and interfacing with the Research Agent. The API server ensures low-latency, real-time communication between the client-side application and the Research Agent.


## Web Application(Streamlit)

The Streamlit web application provides anuser-friendly interface for users to interact with the Research Assistant Agent. 
  

## Design Overview

The application follows a microservices architecture, with the API server and Streamlit app serving as independent components communicating through WebSocket connections. This design ensures modularity, scalability, and ease of maintenance. Key design aspects include:

-  **Modularity:** Separation of concerns between the API server and Streamlit app.

-  **Real-time Communication:** WebSocket technology enables real-time bidirectional communication, facilitating instantaneous chat responses.

-  **Configurability:** The application is highly configurable, with options to adjust agent settings, logging configurations, and API integrations through the `config.json` file.

---
  
## Configurability
Research Assistant AI emphasizes configurability to adapt to diverse needs. Here's how configurability is achieved:

- **Config File**: The `config.json` file centralizes all configuration settings, including agent parameters, tool configurations, API URLs, and logging preferences.
  
- **Agent and Tools Customization**: New agents and tools can be easily added by defining them in the config file and implementing the corresponding agent and tool files. The API server uses the `config.json` to select the agent, and the agent will use the `config.json`  to select the tools. Also, the agents and tools are designed as classes, so it can allow for future inheritence. 
  

## Scalability
The project is built with scalability in mind to accommodate growing demands. Here's how it supports scalability:

- **Async Support**: By using asynchronous operations with FastAPI and Websockets, the application can handle multiple concurrent connections efficiently.
  
- **Docker Containerization**: The application can be easily containerized using Docker, ensuring consistency across environments.
  
- **Cloud Deployment (Google Cloud Run)**: The project has been on Google Cloud Run which provides auto-scaling capabilities. 

## Future Steps
 - Add more agents and tools 
 - Testing
 - CI/CD
 - Caching or Query bector database for scalability
 - Improve web interface

