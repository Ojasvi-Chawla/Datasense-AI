# Datasense-AI
AI-Powered Automated Data Analysis & Visualization Platform

Upload a dataset. Clean it. Analyze it. Visualize it. Ask questions. Generate insights — all without writing code.

DataSense AI is an automated data analysis platform built with Python and Streamlit, designed to make data analysis accessible to students, analysts, business users, and anyone who wants to extract meaningful insights from data without manually performing every step.

 # What is DataSense AI?

DataSense AI provides an end-to-end data analysis workflow in a single platform.

Upload a CSV, Excel, or JSON dataset and use the platform to:

📊 Understand your dataset

🧹 Clean and preprocess data

🔎 Detect and treat outliers

📈 Create interactive visualizations

🖥️ Generate an automated dashboard

🤖 Get AI-powered insights

💬 Ask questions about your data using a chatbot

📄 Generate a professional PDF analysis report

The goal is simple:

Turn raw data into meaningful insights with minimal technical effort.


 # Features
 
- 📁 Upload & Data Quality Score
- Supports CSV, Excel (.xlsx), and JSON
- Instant dataset preview
- Row and column summary
- Automatic Data Quality Score (0–100)
- Quality evaluation across 7 dimensions:
- Completeness
- Accuracy
- Uniqueness
- Consistency
- Validity
- Timeliness
- Integrity

# Data Cleaning

Clean your dataset through an interactive interface without writing code.

-Handle missing values using

-Mean

-Median

-Mode

-KNN Imputer

-Remove duplicate rows

-Correct data types

-Column-level cleaning controls

-Download the cleaned dataset as CSV

# Outlier Detection

Detect unusual observations using multiple statistical and machine-learning techniques.

-Detection Methods

-IQR (Interquartile Range)

-Z-Score

-Isolation Forest

-Treatment Options

-Remove outliers

-Cap/Winsorize outliers

-Replace with Median

Outliers can also be visualized using box plots and scatter plots.

# Exploratory Data Analysis

Automatically explore the structure and statistical characteristics of your dataset.

Includes:

-Descriptive statistics

-Distribution analysis

-Histograms

-KDE plots

-Correlation analysis

-Pearson correlation heatmap

-Categorical frequency analysis

-Missing-value visualization

# Interactive Visualizations

Create interactive charts without writing Python code.

Supports 10+ Plotly chart types, including:

-Bar Chart

-Scatter Plot

-Line Chart

-Histogram

-Box Plot

-Pie Chart

-Heatmap

-Area Chart

-Violin Plot

-Bubble Chart

Users can select columns, grouping options, and visualization settings interactively.

# Automated Dashboard

Generate an analytics dashboard with one click.

The dashboard includes:

-KPI cards

-Key metrics

-Automatically selected charts

-Heatmaps

-Dataset-level summaries

-Quick navigation across analysis modules

The objective is to provide a quick overview of the most important information in a dataset.

# AI Insights

DataSense AI combines rule-based analysis with Gemini 3 Flash Preview to generate meaningful insights from the dataset.

The insight engine can identify:

📈 Trends

⚠️ Anomalies

🔥 Important patterns

📊 Significant variations

💡 Opportunities

🚨 Potential risks

The hybrid approach allows the platform to perform direct analytical checks while using the LLM to generate a natural-language interpretation of the findings.

# AI Data Chatbot

Interact with your dataset using natural language.

Instead of manually searching through tables, users can ask questions such as:

"What is the average sales value?"

"Which category has the highest revenue?"

"What are the major trends in this dataset?"

The chatbot uses a hybrid response system:

Rule-based logic for direct factual/statistical queries

- Gemini 3 Flash Preview for complex and open-ended questions

.Dataset-aware context for more relevant responses

.Conversation history within the session

# AI-Powered PDF Report

Generate a professional data analysis report automatically.

The report can include:

-Executive Summary

-Dataset Overview

-Key Findings

-Visualizations

-Conclusions

-Recommendations

The report is generated using Gemini 3 Flash Preview via Gemini API and exported as a formatted PDF using ReportLab.

# How to Use

Launch DataSense AI.

Upload a CSV, Excel, or JSON dataset.

Review the dataset preview and Data Quality Score.

Clean the dataset if required.

Explore the data using EDA and Visualizations.

Detect and treat outliers.

Generate the automated Dashboard.

Explore AI Insights.

Ask questions through the AI Chatbot.

Generate and download the professional PDF report.

- Complete Workflow

Upload Dataset
      ↓
      

Data Quality Assessment
      ↓

Data Cleaning
      ↓

EDA & Visualization
      ↓

Outlier Detection
      ↓

Automated Dashboard
      ↓

AI Insights
      ↓

AI Chatbot
      ↓

Professional PDF Report

# Environment Variables

- Variable = GEMINI_API_KEY

The API key is required for:

AI Insights

AI Chatbot

AI-powered Report Generation

Core analysis features such as cleaning, EDA, visualization, and outlier detection can operate without the LLM functionality.

# Main Dependencies

streamlit

pandas

numpy

plotly

seaborn

matplotlib

scikit-learn

scipy

google-generativeai

reportlab

openpyxl

python-dotenv

Make sure the package names and versions match your actual requirements.txt before publishing.

# Project Background

DataSense AI was developed as my BCA Major Project at:

Institute of Information Technology & Management (IITM)
Affiliated with Guru Gobind Singh Indraprastha University (GGSIPU)

The project was created to combine concepts from:

Data Analysis

Data Cleaning

Exploratory Data Analysis

Data Visualization

Machine Learning

Generative AI

Natural Language Interaction

Software Development

It allowed me to build an end-to-end application rather than working on individual analysis notebooks or isolated models.

# Future Improvements

Potential areas for future development include:

🔮 Predictive analytics and forecasting

📊 More advanced dashboard customization

🗄️ Database connectivity

☁️ Cloud deployment

👥 Multi-user support

📤 Additional export formats

🤖 More advanced AI-assisted analysis

🔗 Integration with external data sources

 # Contributing

Contributions, issues, and feature requests are welcome.

Fork the repository

Create a feature branch

- git checkout -b feature/AmazingFeature

Commit your changes

- git commit -m "Add AmazingFeature"

Push the branch

- git push origin feature/AmazingFeature

Open a Pull Request

# License

This project is licensed under the MIT License.

See the LICENSE file for details.

# Author

Ojasvi Chawla

BCA — Computer Science & Engineering

IITM, Janakpuri, New Delhi

Affiliated with GGSIPU

# Support

If you found DataSense AI interesting or useful, consider giving the repository a ⭐ star on GitHub.

Your feedback and suggestions are always welcome!


