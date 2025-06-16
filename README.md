# VLSI Architecture Expert Assistant

An AI-powered tool for exploring and modifying VLSI architecture diagrams.

## Features

- 🔍 Search and fetch VLSI architecture diagrams
- 🤖 AI-powered image analysis with LLaVA model
- ✏️ Real-time image modifications
- 🌐 Interactive web interface
- 💾 Download modified architectures

## Prerequisites

- Python 3.8+
- Ollama with LLaVA model installed
- Internet connection

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <git@github.com:ESWARARAO123/soc-architecture.git>
   cd soc-architecture
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Ollama service:**
   ```bash
   ollama run llava
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
soc-architecture/
├── app.py          # Main Streamlit application
├── scraper.py      # Image search functionality
├── vlm.py          # Vision Language Model integration
├── utils.py        # Utility functions
├── assets/         # Generated images directory
└── requirements.txt # Project dependencies
```

## Usage

1. Enter a VLSI architecture name (e.g., "RISC-V CPU block diagram")
2. Click "Fetch Image" to retrieve the diagram
3. Enter modification requests in the prompt box
4. Review the AI-generated modifications
5. Download the modified image if satisfied

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more informatiom