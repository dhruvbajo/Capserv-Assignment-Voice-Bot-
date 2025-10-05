🧠 Voice Bot Service

A minimal Voice-Style Bot Service that:

Accepts a text transcript (simulating speech-to-text output)

Classifies user intent (Lead Creation, Visit Scheduling, Lead Update)

Extracts key entities from the transcript

Interacts with mock CRM APIs to perform actions like lead onboarding, visit scheduling, and lead status updates

--------------------------------------------------------------------------------------------------------------------

⚙️ Features

Built using FastAPI

Simple and modular architecture

Integration with mock CRM APIs

Comprehensive unit tests (pytest)

Supports error handling and validation

Includes example cURL commands for testing

-------------------------------------------------------------------------------------------------------------------------

🚀 Setup & Run Instructions

1️⃣ Prerequisites

Ensure you have the following installed:
Python 3.10+
pip
virtualenv (recommended)

2️⃣ Clone the Repository

git clone <your-repo-url>
cd voice_bot

3️⃣ Create and Activate Virtual Environment
python -m venv venv
On Windows
venv\Scripts\activate
On macOS/Linux
source venv/bin/activate

4️⃣ Install Dependencies
pip install -r requirements.txt

5️⃣ Run the Mock CRM Service
In one terminal:
uvicorn mock_crm:app --host 0.0.0.0 --port 8001 --reload

6️⃣ Run the Voice Bot Service
Open another terminal and run:
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

7️⃣ Run Unit Tests
In a new terminal:
pytest -v

--------------------------------------------------------------------------------------------------------------------
📡 Example cURL Commands

✅ Lead Creation
curl -X POST http://127.0.0.1:8000/bot/handle -H "Content-Type: application/json" -d "{\"transcript\":\"Create lead John Doe email john@example.com phone 9876543210 from Mumbai source Instagram\"}"

✅ Visit Scheduling
curl -X POST http://127.0.0.1:8000/bot/handle -H "Content-Type: application/json" -d "{\"transcript\":\"Schedule a visit for lead 123e4567-e89b-12d3-a456-426614174000 on 10th Oct 2025 at 4 PM with notes Discuss requirements\"}"

✅ Lead Update
curl -X POST http://127.0.0.1:8000/bot/handle -H "Content-Type: application/json" -d "{\"transcript\":\"Update lead 7b1b8f54-aaaa-bbbb-cccc-1234567890ab to WON notes booked unit A2\"}"

------------------------------------------------------------------------------------------------------------------------

🧪 Example Test Run Output

<img width="1193" height="450" alt="image" src="https://github.com/user-attachments/assets/ab9d70dc-13e7-45ac-b9ab-4d9400c841f7" />


-------------------------------------------------------------------------------------------------------------------------

Lead Creation curl command output:
![Uploading image.png…]()


Visit schedule curl command output:
![Uploading image.png…]()


Lead update curl command output:
![Uploading image.png…]()


------------------------------------------------------------------------------------------------------------------------

With more time, I would enhance NLU and LLM integration to handle complex queries, improve casual datetime parsing, add robust CRM retries and error handling, implement structured analytics logging, support multi-intent processing, and provide a simple frontend or mobile demo for easier integration. Dockerization for reproducible setup would also be added.
