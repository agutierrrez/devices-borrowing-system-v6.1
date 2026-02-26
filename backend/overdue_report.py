from backend import db
from backend.models import Laptop
from datetime import datetime, timezone
import os
from backend.emailer import send_email


def generate_overdue_report(output_path=None, send_emails=False):
    # Use timezone-aware UTC now, then convert to naive UTC for DB comparisons
    now_aware = datetime.now(timezone.utc)
    now = now_aware.replace(tzinfo=None)
    overdue = Laptop.query.filter(Laptop.is_borrowed == True, Laptop.due_date != None, Laptop.due_date < now).all()
    lines = []
    results = []
    for l in overdue:
        line = f'{l.name}, borrowed by {l.borrower}, due {l.due_date.isoformat()}'
        lines.append(line)
        if send_emails and l.borrower_email:
            subject = f'Overdue device: {l.name}'
            body = f'Hello {l.borrower},\n\nThe device {l.name} was due on {l.due_date.isoformat()} and is overdue. Please return it as soon as possible.\n\nThanks.'
            try:
                ok = send_email(l.borrower_email, subject, body)
                results.append((l.borrower_email, ok))
            except Exception as e:
                results.append((l.borrower_email, False, str(e)))

    report = '\n'.join(lines)
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
    # Print the report and email results
    print('--- Overdue Report ---')
    if report:
        print(report)
    else:
        print('No overdue items')
    if send_emails:
        print('\n--- Email send results ---')
        for r in results:
            print(r)
    return report, results


if __name__ == '__main__':
    out = os.environ.get('OVERDUE_REPORT_PATH', 'overdue_report.txt')
    send_emails = os.environ.get('OVERDUE_SEND_EMAILS', '0') in ('1', 'true', 'yes')
    with db.session.begin():
        generate_overdue_report(out, send_emails=send_emails)
    print(f'Report written to {out}')
