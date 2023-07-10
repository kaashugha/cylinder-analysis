---

# Flask App Documentation

This is the main Flask application file (`app.py`) for the project. It contains the implementation of the Flask routes and handles various HTTP requests.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Routes](#routes)
  - [Homepage (`/`)](#homepage)
  - [User Login (`/login/`)](#user-login)
  - [User Registration (`/register/`)](#user-registration)
  - [Ticket Generation and Management (`/ticket/`)](#ticket-generation-and-management)
  - [Drop-off Tracking and Analysis (`/drop-off/`)](#drop-off-tracking-and-analysis)
  - [Cylinder Analysis (`/cylinder-analysis/`)](#cylinder-analysis)
  - [Cylinder Breaking (`/cylinder-breaking/`)](#cylinder-breaking)
  - [Report Generation (`/create-report/`)](#report-generation)
  - [Logout (`/logout/`)](#logout)
  - [Calendar Integration (`/calendar/`)](#calendar-integration)
  - [Ticket Creation Success (`/ticket_success/`)](#ticket-creation-success)
  - [Drop-off Success (`/dropoff_success/`)](#drop-off-success)
  - [Client Specific Static Website Pages] (#Client-Specific-Static-Website-Pages)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Make sure you have the following software installed on your system:

- Python 3.x
- Flask
- MySQL or another compatible database management system

## Installation

1. Clone the repository or download the source code.
2. Install the required Python packages by running the following command in your terminal or command prompt:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a MySQL database and update the database configuration in the `app.py` file.
4. Run the Flask application with the following command:

   ```bash
   flask run
   ```

5. Access the application in your web browser at `http://localhost:5000` (or the specified host and port).

## Usage

The Flask application provides the following functionality:

- User registration and login for lab and field technician accounts.
- Access control and role-based permissions.
- Ticket generation and management.
- Cylinder Drop-off tracking.
- Google Calendar API integration for scheduling cylinder breaking.
- Report generation.

## Routes

The application defines the following routes:

### Homepage (`/`)

- Main landing page for clients website.

### User Login (`/login/`)

- Provides a form for users to enter their login credentials.
- Handles the login process by validating the user's credentials.
- If the login is successful, redirects the user to the appropriate dashboard based on their role (admin, lab technician, or field technician).
- If the login fails, displays an error message and allows the user to try again.

### User Registration (`/register/`)

- Requires user authentication (Admin)
- Provides a form for users to create a new lab or field accounts.
- Handles the registration process by validating the form data and creating a new user in the database.
- If the registration is successful, redirects the user to the login page.
- If the registration fails (e.g., due to an existing username), displays an error message and allows the user to try again.

### Ticket Generation and Management (`/ticket/`)

- Requires user authentication (Lab, Field, Admin).
- Provides a form for generating new tickets with various details such as client information, site address, load number, etc.
- Validates the form data and creates a new ticket for batch of cylinders (able to create multiple cylinders with different breaking dates from one batch) in the database.
- Assigns a unique batch ID to each ticket.
- Creates an event in the Google Calendar for ticket breaking date.

### Drop-off Tracking and Analysis (`/drop-off/`)

- Requires user authentication (Lab, Field, Admin).
- Provides a form for tracking drop-offs of certain items or materials.
- Records the drop-off timestamp and the user responsible for the drop-off in the corresponding ticket entry.
- Changes the color in the Google Calendar for each cylinder in the batch (potentially across different days) to show that the cylinder has been dropped off in the lab.

### Cylinder Analysis (`/cylinder-analysis/`)

- Requires user authentication (Lab, Admin).
- Provides a form for analyzing cylinders, including parameters like weight, height, and diameter.
- Allows authorized users to update the cylinder analysis data in the database.

### Cylinder Breaking (`/cylinder-breaking/`)

- Requires user authentication (Lab, Admin).
- Provides a form for recording the breaking of cylinders, including parameters like compressive strength and fracture type.
- Allows authorized users to update the cylinder breaking data in the database.

### Report Generation (`/create-report/`)

- Requires user authentication (Lab, Admin).
- Provides a form for generating reports based on specific criteria (e.g., batch ID, date range, client, etc.).
- Generates PDF report and stores them in a designated directory within the EC2 instance.
- Downloads the generated reports to the users system.
- Deletes the reports from the EC2 instance.

### Logout (`/logout/`)

- Logs out the currently authenticated user and redirects them to the login page.

### Calendar Integration (`/calendar/`)

- Requires user authentication (Lab, Admin).
- Integrates with Google Calendar to display and manage scheduled events.
- Allows authorized users to view and manage calendar events.

### Ticket Creation Success (`/ticket_success/`)

- Requires user authentication (Lab, Field, Admin).
- Displays a success page after successfully creating a new ticket.
- Provides the batch ID and other relevant details of the created ticket for field technician to record.

### Drop-off Success (`/dropoff_success/`)

- Requires user authentication (Lab, Field, Admin).
- Displays a success page after successfully recording a drop-off.
- Provides the batch ID and other relevant details of the drop-off.

### Client Specific Static Website Pages

Renders the following html pages for site funtionality. Outside the scope of the cylinder analysis software.

- About Us (`/about-us/`)
- Careers (`/careers/`)
- Contact Us (`/contact-us/`)
- Projects (`/projects/`)
- Services (`/services/`)

## Dependencies

The Flask application relies on the following dependencies (specified in `requirements.txt`):

- Flask - The web framework used for developing the application.
- MySQL Connector - A Python driver for MySQL to connect to the database.
- bcrypt - A password hashing library for secure password storage.
- google-auth - A library for Google authentication and API access.
- google-api-python-client - A client library for accessing Google APIs.
