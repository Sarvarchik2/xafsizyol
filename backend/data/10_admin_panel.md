# Admin Panel Guide

## Accessing the Admin Panel

The admin panel is available at /admin in the web app.
Access requires a password (set by the system administrator).
Admin routes are protected by the admin-auth middleware.

## Admin Dashboard (/admin/dashboard)

Shows key statistics:
- Total number of reports submitted
- Number of reports with Pending status
- Number of reports with In Progress status
- Number of reports with Fixed status
- Recent activity overview

## Admin Reports Table (/admin/reports)

- View all reports in a table format
- Each row shows: ID, address, severity, status, submission date, vote count
- Ability to update the status of any report:
  - Change from Pending to In Progress
  - Change from In Progress to Fixed
  - Change back to any status if needed
- When an admin updates a status, the report owner automatically receives a Telegram notification
- Filter and search reports

## Admin Map (/admin/map)

- Interactive map showing all reports
- Click any marker to see report details
- Update report status directly from the map popup
- Useful for understanding geographic distribution of problems
- Can identify areas with concentrated road damage

## Status Update Notifications

When an admin changes a report status:
1. The database is updated immediately
2. If the report has a valid Telegram userId (numeric), a notification is sent automatically:
   - "In Progress": "Ko'rib chiqilmoqda" notification
   - "Fixed": "Bajarildi" notification
3. The notification includes the report address and new status

## Admin Authentication

- Admin login page at /admin (index)
- Password-based authentication
- Session stored in browser (no server-side session)
- Middleware checks admin auth on all /admin/* routes except /admin itself
- If not authenticated, redirects to /admin login page
