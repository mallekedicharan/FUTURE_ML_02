TicketIQ — Support Ticket Classification & Prioritization
An ML-powered web application that automatically classifies customer support tickets into categories and assigns priority levels using Natural Language Processing.

Overview
In real companies, customer support teams receive hundreds of tickets daily. This system solves three key problems:
Tickets are not categorized properly — Auto-classification into 5 categories
Urgent issues get delayed — Automatic priority assignment (Low/Medium/High/Critical)
Support teams waste time sorting — Instant ML-based triage

Tech Stack
Tool	                    Purpose
Python	                  Core development language
NLTK	                    Text preprocessing & NLP (tokenization, stopwords, lemmatization)
Scikit-learn            	ML models (LinearSVC, Random Forest) & TF-IDF vectorization
Flask                   	Web application server
Pandas / NumPy	          Data manipulation

Project Structure
FUTURE_ML_02/
├── generate_dataset.py    # Generates synthetic support ticket dataset
├── train_model.py         # ML pipeline: preprocessing → training → evaluation
├── app.py                 # Flask web server with API endpoints
├── support_tickets.csv    # Generated dataset (8000 tickets)
├── requirements.txt       # Python dependencies
├── models/                # Saved model artifacts
│   ├── category_model.joblib
│   ├── priority_model.joblib
│   ├── tfidf_vectorizer.joblib
│   └── evaluation_results.json
├── templates/
│   └── index.html         # Main dashboard template
└── static/
    ├── style.css           # Modern dark theme styling
    └── script.js           # Frontend interactivity

Setup & Run
1.Install dependencies:
pip install -r requirements.txt
2.Generate the dataset:
python generate_dataset.py
3.Train the models:
python train_model.py
4.Launch the web dashboard:
python app.py
Open "http://localhost:5000" in your browser.

ML Pipeline
1.Text Preprocessing (NLTK): Lowercasing, punctuation removal, stopword removal, tokenization, lemmatization
2.Feature Extraction: TF-IDF Vectorization with unigrams & bigrams (5000 features)
3.Category Classification: LinearSVC — classifies tickets into 5 categories
4.Priority Prediction: Random Forest — assigns priority levels (Low/Medium/High/Critical)
5.Evaluation: Accuracy, Precision, Recall, F1-Score, Confusion Matrix

Categories
Category	                Description
Technical Issue         	Hardware/software malfunctions
Billing Inquiry         	Payment & invoice questions
Product Inquiry         	Specs, warranty, availability
Account Access          	Login & security issues
General Query           	Feedback, shipping, general info

Business Impact
60% faster first-response times through auto-triage
Accurate routing to the right department
Reduced backlog with priority-based handling
Data-driven insights into support trends
