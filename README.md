# leavi (plain old web app)

leavi is a simple web application that allows users to manage leaves and absences. It provides a user-friendly interface for employees to submit leave requests, view their leave balance, and track the status of their requests. Administrators can approve or reject leave requests and manage employee leave records.

## Features

- Employee leave request submission
- Leave balance tracking
- Request status monitoring
- Administrator approval workflow
- E-Mail notifications for request updates
- Nudge feature for pending requests

## Technologies Used

- uv (package manager)
- Python
- Django
- HTML/CSS
- Tailwind CSS
- Alpine.js
- Postgresql

## Installation

1. Clone the repository

```bash
git clone https://github.com/Hullaah/leavi.git
```

2. Install dependencies

```bash
uv sync --locked
```

3. Set up the database

```bash
uv run manage.py migrate
```

4. Configure environment variables using a `.env` file or export them in your shell

```bash
DB_NAME=leavi_powa
DB_USER=leavi_user
DB_PASSWORD=leavi_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key
```

5. Run the application

In two separate terminal windows, run the following commands to start the development server and the tailwind watcher:

```bash
uv run manage.py runserver
```

```bash
uv run manage.py tailwind start
```

## Usage

To use leavi, follow these steps:

1. Navigate to the application's URL
2. Log in with your credentials
3. Submit a leave request or view your leave balance
4. Monitor the status of your requests
5. Contact administrators for any inquiries
