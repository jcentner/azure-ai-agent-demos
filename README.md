# Azure AI Foundry Agents Demos

This repository contains sample code and instructions for creating a variety of simple Azure AI Foundry Agents. Demos include those for using tools like Grounding with Bing Search, MCP servers, and OpenAPI schemas. Also included are walkthroughs for enterprise features like observability, secure networking, and more.

## Index of Demos

- [/mcp_github_agent](/mcp_github_agent): Using an MCP tool to connect to the GitHub public preview MCP server, either with a Personal Authentication Token or using an OAuth app. 
- [/docs_agent](/docs_agent): Using multiple tools (MCP + Bing Grounding) to create an agent grounded by Microsoft Learn documentation for Azure and Microsoft managed GitHub repositories. 
- [/otel_observable_agent](/otel_observable_agent): Integration with OpenTelemetry and Azure App Insights for observability, as well as extreme verbosity in output for debugging. 

## TODO

- [x] Demo for GitHub MCP public preview server with PAT
- [ ] Demo for GitHub MCP with OAuth
- [ ] Demo for GitHub MCP + Bing Grounding ("docs" demo, multi-tool)
- [ ] Observability demo building on the docs demo above
- [ ] Copilot studio integration with Azure AI Foundry Agent demo 
- [ ] More!