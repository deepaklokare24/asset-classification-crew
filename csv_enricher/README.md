# CSV Data Enrichment with CrewAI

This application uses CrewAI agents with CSV RAG Search to fill missing data in user-uploaded CSV files.

## Features

- Upload CSV files with missing asset categorization values
- AI-powered data enrichment using CrewAI agents with CSV RAG Search
- Semantic search capabilities using Hugging Face embeddings (runs locally)
- Real-time progress tracking
- Download enriched CSV files with filled values
- Automatic category matching using Cluster IDs

## Setup

1. Clone this repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   If you encounter any issues with the installation, you can try installing directly:
   ```bash
   pip install 'crewai[tools]' fastapi uvicorn streamlit python-multipart pandas anthropic sentence-transformers torch transformers langchain-huggingface python-dotenv tqdm
   ```

4. Install Hugging Face models:
   ```bash
   python install_huggingface.py
   ```
   This script will download and cache the Hugging Face models locally, making them available for offline use.

   **For environments with SSL certificate issues:**
   
   If you encounter SSL certificate errors when downloading models, follow these steps:
   
   a. On a machine with internet access:
   ```bash
   python download_huggingface_model.py
   ```
   This will download the model and create a zip file in the `models` directory.
   
   b. Transfer the model directory or zip file to your restricted environment.
   
   c. On the restricted machine:
   ```bash
   python install_local_huggingface.py models/sentence-transformers/all-MiniLM-L6-v2
   ```
   This will set up the model for local use without requiring internet access.

5. Create a `.env` file with your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
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

The application uses CrewAI's CSV RAG Search tool with Anthropic Claude and Hugging Face embeddings to semantically search through a source CSV file and find relevant information to fill in missing values in the uploaded CSV file. The process involves three specialized agents:

1. **CSV Data Analyzer**: Analyzes the input CSV file to identify missing data and understand the data structure
2. **Data Enrichment Specialist**: Uses the CSV RAG Search tool to find appropriate category values for rows with missing data and directly processes the CSV file using code execution
3. **Data Quality Assurance Specialist**: Verifies the quality and consistency of the enriched data

These agents work together in a sequential process, with each agent building on the work of the previous one.

### Improved Enrichment Process

The application now includes an improved enrichment process that uses multiple strategies to fill in missing category values:

1. **Cluster-Based Matching**: The application first tries to match products based on their Cluster ID, which groups similar products together. If one product in a cluster has category information, it applies that information to other products in the same cluster.

2. **Semantic Search**: For products that can't be matched by Cluster ID, the application uses semantic search to find similar products in the source CSV file and extracts category information from the search results.

3. **Fallback Mechanism**: If the agent-based enrichment fails, the application uses a fallback mechanism that directly processes the CSV file to ensure that all possible enrichments are applied.

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

## Why Hugging Face Embeddings?

We use Hugging Face embeddings for semantic search capabilities. Hugging Face provides high-quality, open-source models that can run entirely locally without requiring external API calls. This makes it ideal for environments with restricted network access or privacy requirements.

The `sentence-transformers/all-MiniLM-L6-v2` model we use is:
- Lightweight (only ~80MB)
- Fast to run, even on CPU
- Provides excellent semantic search capabilities
- Works completely offline once downloaded
- Produces 384-dimensional embeddings that capture semantic meaning well

All models are downloaded and cached locally during installation, so no internet connection is required during operation.

## Working in Restricted Network Environments

If you're working in an environment with restricted network access or SSL certificate issues, follow these steps:

1. **Download the model on a machine with internet access:**
   ```bash
   python download_huggingface_model.py
   ```
   This creates a portable model package in the `models` directory and a zip file for easy transfer.

2. **Transfer the model to your restricted environment:**
   - Copy the entire `models/sentence-transformers/all-MiniLM-L6-v2` directory, or
   - Transfer the zip file `models/sentence-transformers_all-MiniLM-L6-v2.zip` and extract it

3. **Install the model locally:**
   ```bash
   python install_local_huggingface.py models/sentence-transformers/all-MiniLM-L6-v2
   ```
   This sets up the model in the Hugging Face cache directory without requiring internet access.

4. **Verify the installation:**
   The script will automatically verify that the model can be loaded and used.

5. **Run the application as normal:**
   ```bash
   python run.py
   ```

## Testing

You can test the application using the provided test script:
```
python test_enrichment.py
```

This will run the CSV enrichment process on the sample input file and verify that it works correctly.

## Troubleshooting

- If you encounter dependency conflicts during installation, try the direct installation method mentioned in the Setup section.
- Make sure you have set the correct API keys in the `.env` file.
- Ensure that the source CSV file is correctly placed in the data directory.
- If you're experiencing issues with the CSV RAG Search tool, try adjusting the configuration in the `csv_enrichment_crew.py` file.
- If you see import errors, make sure you're running the application using the `run.py` script.
- If you encounter issues with Hugging Face models:
  - Run `python install_huggingface.py` again to ensure all models are downloaded
  - Check your system's CUDA configuration if you have a GPU
  - For CPU-only systems, no special configuration is needed
  - For SSL certificate errors, use the offline installation method described above
- If you see an error about missing `langchain-huggingface`, install it with:
  ```bash
  pip install langchain-huggingface
  ```
- If the embedding process is taking too long:
  - The first run will be slower as it needs to load the model into memory
  - Subsequent runs should be faster
  - Consider using a smaller model if performance is an issue

## License

This project is licensed under the MIT License - see the LICENSE file for details. 