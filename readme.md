# Bauhaus Watch - Open Source Search Engine for University Committee Protocols

![Search Engine](documentation/search_gips.png)

## Introduction

Bauhaus Watch is an open-source search engine specifically designed for indexing and searching protocols of university committees. It provides an efficient and user-friendly way to access and retrieve information from various committee meetings, making it easier for students, lecturers, and administrators to stay informed about the decisions and discussions within the university's governing bodies.

## Features

- [X] **Protocol Indexing**: Bauhaus Watch automatically indexes protocols from university committee sessions, making them easily searchable.

- [X] **Keyword Highlighting**: Bauhaus Watch highlights search keywords within the protocols, helping users identify relevant sections.

- [X] **User-Friendly Interface**: The user interface is designed to be intuitive, allowing users of all levels of technical expertise to navigate and use the search engine effortlessly.

- [X] **Format Independent**: The search functionality does not depend on a specific format of the PDF as long as the text is selectable. Therefore committees do not need to change their protocol template.

- [X] **Autonomous Updates**: Bauhaus Watch fetches new protocols on it's own, making new information available as soon as it is published on the committee website.

- [ ] **Customizable Filters**: Users can apply filters based on committees, dates, or specific topics to narrow down search results.

## Development Setup with VS Code Dev Containers

For the best development experience, use VS Code Dev Containers. This provides:
- A consistent development environment
- Live code editing without rebuilding containers
- Direct access to Elasticsearch
- All dependencies pre-installed

### Quick Start (Dev Container)

1. **Prerequisites**:
   - Install VS Code
   - Install the "Dev Containers" extension in VS Code
   - Install Docker

2. **Setup Development Environment**:
   ```bash
   ./dev-setup.sh
   ```

3. **Open in Dev Container**:
   - Open VS Code
   - Press `Ctrl+Shift+P` and run `Dev Containers: Reopen in Container`
   - Or use the command palette: `Dev Containers: Open Folder in Container`

4. **Run the Application**:
   Inside the dev container terminal:
   ```bash
   ./dev-run.sh
   ```
   
   Or manually:
   ```bash
   python app.py
   ```

5. **Access the Application**:
   - Web App: http://localhost:8001
   - Elasticsearch: http://localhost:9200

### Development Features

- **Live Code Editing**: Changes to your code are immediately reflected
- **Hot Reload**: Flask development server with auto-reload
- **Integrated Terminal**: Full terminal access inside the container
- **Debugging**: Set breakpoints and debug directly in VS Code
- **Linting & Formatting**: Pre-configured with flake8 and black
- **Git Integration**: Full git support inside the container

## Search Engine Configuration

This application supports two search engines:

### 1. PDFSearch (Default)
The original search engine that searches through PDF documents directly.

### 2. Elasticsearch
A more powerful search engine that provides better search capabilities, highlighting, and scoring.

## Configuration

To switch between search engines, modify the `application.json` file:

```json
{
    "search_engine": "pdfsearch",  // or "elasticsearch"
    "elasticsearch": {
        "hosts": ["http://localhost:9200"],
        "index": "protocols",
        "timeout": 30
    }
}
```

## Elasticsearch Setup

### Option 1: Containerized Setup (Recommended)

1. The application now includes Elasticsearch in the Docker setup
2. Run the rebuild script to set up everything:
   ```bash
   ./rebuild_elasticsearch.sh
   ```

This will:
- Build a new Docker image with Elasticsearch support
- Start Elasticsearch and the application containers
- Automatically load all protocols from `app/downloads` into Elasticsearch
- Make the application available at `http://localhost:5303`
- Make Elasticsearch available at `http://localhost:9200`

### Option 2: Manual Setup

1. Install Elasticsearch dependency:
   ```bash
   pip install elasticsearch==8.11.0
   ```

2. Set up an Elasticsearch instance and create an index named "protocols"

3. Index your protocol data with the following structure:
   ```json
   {
     "title": "Protocol Title",
     "committee": "Committee Name", 
     "date": "2024-01-01",
     "content": "Full protocol content..."
   }
   ```

4. Change the search engine in `application.json`:
   ```json
   {
     "search_engine": "elasticsearch"
   }
   ```

## Search Endpoints

- `/search` - Uses the configured search engine (default: elasticsearch)
- `/search/pdfsearch` - Always uses PDFSearch
- `/search/elasticsearch` - Always uses Elasticsearch

## Getting Started

There is a test server running at [bauhauswatch.ludattel.info](https://bauhauswatch.ludattel.info)

### Requirements

- Docker

### Installation

1. Clone the repository: `git clone https://github.com/henicosa/BauhausWatch.git`
2. Install and run docker container: `./install.sh`

### Usage

1. Access the search engine through the web browser at `http://localhost:5303`.
2. Enter your search query in the search bar.
3. Click on the page information on a search result to view the full committee protocol.

Because of legal reasons you need to retrieve your own data. The application is designed to be accessed solely from inside the university network. You can turn off this safety measure by setting the variable `development_mode` to `true` in `app.py`.

## Contribution Guidelines

I welcome contributions from the community to improve and enhance Bauhaus Watch. If you would like to contribute, please follow these guidelines:

1. Fork the repository and create your branch: `git checkout -b my-feature`
2. Make changes and commit them: `git commit -m "Add feature"`
3. Push to your branch: `git push origin my-feature`
4. Open a pull request with a detailed description of the changes.

## License

Bauhaus Watch is open-source software licensed under the [MIT License](LICENSE).

## Feedback and Support

If you encounter any issues, have suggestions, or need support, please open an issue on the repository. I appreciate your feedback and am committed to making Bauhaus Watch better with your help!

---

Thank you for using Bauhaus Watch! I hope this search engine will be a valuable resource for accessing university committee protocols and staying informed about the decisions that shape our academic community. Happy searching!
