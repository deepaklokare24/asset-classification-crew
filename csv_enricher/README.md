# CSV Data Enrichment with CrewAI

This application uses CrewAI agents with CSV RAG Search to fill missing data in user-uploaded CSV files.

## Features

- Upload CSV files with missing asset categorization values
- AI-powered data enrichment using CrewAI agents with CSV RAG Search
- Semantic search capabilities using Ollama embeddings (runs locally)
- Real-time progress tracking
- Download enriched CSV files with filled values

## Setup

1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Ollama:
   - You can use our installation script which will install Ollama and the required embedding model:
     ```bash
     python install_ollama.py
     ```
   - Or follow the instructions at [ollama.ai](https://ollama.ai) to install Ollama manually
   - Make sure the Ollama service is running
   - Pull the embedding model: `ollama pull nomic-embed-text`
   - Make sure the Ollama service is running:
     ```bash
      ollama serve
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   If you encounter any issues with the installation, you can try installing directly:
   ```bash
   pip install 'crewai[tools]' fastapi uvicorn streamlit python-multipart pandas anthropic ollama==0.4.7 langchain-anthropic python-dotenv tqdm
   ```

5. Create a `.env` file with your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   # No additional API keys needed for Ollama as it runs locally
   ```
6. Run the setup script to copy the source CSV file:
   ```
   python setup.py
   ```

## Running the Application

You can run the application using the run script:

```bash
python run.py
```

This will start both the backend server and the frontend application.

### Command-line Options

- `--backend-only`: Start only the backend server
- `--frontend-only`: Start only the frontend application

Example:
```bash
python run.py --backend-only
```

## Using the Application

1. Open your browser and navigate to http://localhost:8501
2. Upload a CSV file with missing category values
3. Optionally specify the category column names (comma-separated)
4. Click "Process File" to start the enrichment process
5. Wait for the processing to complete
6. Download the enriched CSV file

## Project Structure

- `backend/`: FastAPI backend service
- `frontend/`: Streamlit frontend application
- `agents/`: CrewAI agent definitions and crew orchestration
- `utils/`: Utility functions for file handling and progress tracking
- `data/`: Directory for storing CSV files

## How It Works

The application uses CrewAI's CSV RAG Search tool with Anthropic Claude and Ollama embeddings to semantically search through a source CSV file and find relevant information to fill in missing values in the uploaded CSV file. The process involves three specialized agents:

1. **CSV Data Analyzer**: Analyzes the input CSV file to identify missing data and understand the data structure
2. **Data Enrichment Specialist**: Uses the CSV RAG Search tool to find appropriate category values for rows with missing data and directly processes the CSV file using code execution
3. **Data Quality Assurance Specialist**: Verifies the quality and consistency of the enriched data

These agents work together in a sequential process, with each agent building on the work of the previous one.

### Performance Optimization with Caching

The application now includes a caching mechanism for ChromaDB embeddings to significantly improve performance on subsequent runs:

- The first time you process a CSV file, the application creates embeddings for the source CSV file, which can take some time
- These embeddings are cached in a pickle file in the `data/cache` directory
- On subsequent runs, the application checks if a valid cache exists and uses it instead of recreating the embeddings
- This reduces processing time from minutes to seconds for repeated operations
- The cache is automatically invalidated if the source CSV file changes

### Code Execution for Direct CSV Processing

The Data Enrichment Specialist agent is equipped with code execution capabilities, allowing it to:

1. Read the input CSV file using pandas
2. Analyze the data to identify rows with missing values
3. Use the CSV RAG Search tool to find appropriate values for missing fields
4. Write the enriched data directly to the output CSV file

This direct code execution approach ensures more reliable and accurate enrichment compared to parsing agent responses, as the agent can:
- Access and manipulate the data directly
- Apply complex logic to determine appropriate values
- Handle edge cases more effectively
- Ensure all missing fields are properly filled

## Why Ollama Embeddings?

We use Ollama embeddings for semantic search capabilities. Ollama is an open-source project that allows you to run embedding models locally without requiring external API calls. This makes it ideal for environments with restricted network access. The nomic-embed-text model provides high-quality embeddings that work well with our CSV RAG Search tool.

We're using Ollama version 0.4.7, which is the latest stable version as of January 2025.

## Testing

You can test the application using the provided test script:
```
python test.py
```

This will run the CSV enrichment process on the sample input file and verify that it works correctly.

## Troubleshooting

- If you encounter dependency conflicts during installation, try the direct installation method mentioned in the Setup section.
- Make sure you have set the correct API keys in the `.env` file.
- Ensure that the source CSV file is correctly placed in the data directory.
- If you're experiencing issues with the CSV RAG Search tool, try adjusting the configuration in the `csv_enrichment_crew.py` file.
- If you see import errors, make sure you're running the application using the `run.py` script.
- If you encounter issues with Ollama:
  - Ensure the Ollama service is running (`ollama serve`)
  - Verify the nomic-embed-text model is installed (`ollama list`)
  - Check that you have the correct version of the Ollama Python package (`pip show ollama`)
- If you see an error about missing `langchain-anthropic`, install it with:
  ```bash
  pip install langchain-anthropic
  ```
- If the embedding process is taking too long:
  - Check if the cache directory (`data/cache`) exists and has proper permissions
  - You can manually clear the cache by deleting files in the `data/cache` directory
  - If you're processing a very large CSV file, the initial embedding creation will take longer

## License

This project is licensed under the MIT License - see the LICENSE file for details. 