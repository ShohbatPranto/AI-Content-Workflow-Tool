# **🤖 AI Content Workflow Tool**

An advanced web application built with Streamlit, LangChain, and OpenAI to generate and refine high-quality content using a structured, multi-step prompt chaining workflow.

This tool guides users from a simple topic to a fully polished piece of content (blog post, ad copy, etc.) by breaking the creative process into four distinct, editable stages.

## **✨ Key Features**

* **📈 4-Step Chaining Workflow:** Guides users through Idea Generation → Outline → First Draft → SEO & Tone Refinement.  
* **✏️ Fully Editable:** Users can modify the AI-generated text at any step before proceeding to the next.  
* **🤖 Smart Prompting:** Uses simulated few-shot examples (based on tone selection) to maintain a consistent writing style.  
* **⚙️ Configurable Output:** Easily select content type, tone (e.g., *Professional, Witty, Casual*), and approximate word length.  
* **💾 Content History:** All completed workflows, including user scores, are saved to a local SQLite database for review.  
* **⭐ Simple Evaluation:** A built-in scoring system (1-5 stars) for rating the clarity and engagement of the final content.  
* **📥 Export Results:** Download the entire workflow (from idea to final draft) as a .md or .txt file.

## **🛠️ Tech Stack**

* **Frontend:** [Streamlit](https://streamlit.io/)  
* **AI Orchestration:** [LangChain](https://www.langchain.com/) (using the new LCEL standard)  
* **AI Language Model:** [OpenAI API](https://openai.com/) (defaults to gpt-4o-mini)  
* **Database:** [SQLite3](https://www.sqlite.org/index.html) (for local history)  
* **Environment:** [Python 3.10+](https://www.python.org/) & python-dotenv

## **🚀 Getting Started**

Follow these instructions to set up and run the project on your local machine.

### **1. Prerequisites**

* [Python 3.10 or newer](https://www.python.org/downloads/)  
* [Git](https://www.google.com/search?q=https://git-scm.com/downloads)  
* An [OpenAI API Key](https://platform.openai.com/api-keys)

### **2. Clone the Repository**

git clone [https://github.com/your-username/ai-content-workflow-tool.git\](https://github.com/your-username/ai-content-workflow-tool.git)  
cd ai-content-workflow-tool

### **3. Set Up a Virtual Environment**

It is highly recommended to use a virtual environment.

# For macOS/Linux  
python3 -m venv venv  
source venv/bin/activate

# For Windows  
python -m venv venv  
.\venv\Scripts\activate

### **4. Install Dependencies**

Install all required Python packages.

pip install -r requirements.txt

### **5. Set Up Your API Key**

This application requires an OpenAI API key to function.

1. Find the .env.example file in the project's root directory.  
2. Make a copy of this file and rename it to .env:  
   cp .env.example .env

3. Open the new .env file in a text editor.  
4. Paste your secret OpenAI API key into the file:  
   OPENAI_API_KEY="sk-YOUR_SECRET_API_KEY_HERE"

### **6. Run the Application**

With your virtual environment active and your API key in place, start the Streamlit server:

streamlit run app.py

Your default web browser will automatically open to http://localhost:8501, and you can begin using the tool.

## **🤝 Contributing**

Contributions are welcome! If you have suggestions for improvements or new features, please feel free to:

1. **Fork** the repository.  
2. Create a new **feature branch** (git checkout -b feature/AmazingFeature).  
3. **Commit** your changes (git commit -m 'Add some AmazingFeature').  
4. **Push** to the branch (git push origin feature/AmazingFeature).  
5. Open a **Pull Request**.

## **📄 License**

This project is distributed under the MIT License. See the LICENSE file (if you choose to add one) for more details.
