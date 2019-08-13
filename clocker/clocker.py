#!/usr/bin/env python
import argparse
import collections
import datetime
import os
import sys


Record = collections.namedtuple('Record', ('datetime', 'event', 'project'))
WorkPeriod = collections.namedtuple('WorkPeriod', ('start', 'duration', 'project'))

DATETIME_FMT = "%Y-%m-%d %H:%M:%S.%f"


def get_clocker_filename():
    """Get the name of the clocker file from environment variable CLOCKER_FILE.

    If the environment variable is not set, defaults to ``.clocker`` in the
    current directory.

    """
    return os.getenv('CLOCKER_FILE', '.clocker')


def get_records(start=None, end=None):
    """Return a list of records. By default, returns all records."""
    records = []
    start = start or datetime.datetime(1, 1, 1, 0, 0)
    end = end or datetime.datetime.now()
    next_event = 'IN'
    for line in open(get_clocker_filename()):
        dt_str, event, project = [token.strip() for token in line.split(',')]
        dt = datetime.datetime.strptime(dt_str, DATETIME_FMT)
        if dt < start or event != next_event:
            # Move until the first IN event after the start date
            continue
        if event == 'IN' and dt > end:
            # Done processing all relevant records
            break
        records.append(Record(datetime=dt, event=event, project=project))
        next_event = 'IN' if next_event == 'OUT' else 'OUT'
    return records


def get_last_record():
    """Read the last record from the clocker file."""
    try:
        with open(get_clocker_filename()) as clocker_file:
            line = clocker_file.readlines()[-1]
            dt_str, event, proj = [token.strip() for token in line.split(',')]
    except (FileNotFoundError, IndexError):
        return None
    return Record(dt_str, event, proj)


def is_clocked_in():
    """Return True if last entry in clocker file is a clock in event."""
    last_record = get_last_record()
    if last_record and 'IN' in last_record.event:
        return True
    return False


def get_week_boundaries(date=None):
    """Return datetimes for the beginning and end of the week containing the
    given date."""
    date = date or datetime.date.today()
    # Week starts on Sunday, get previous Sunday.
    start = date - datetime.timedelta(date.weekday() + 1)
    # Convert to datetime at 00:00:00.
    start = datetime.datetime(start.year, start.month, start.day)
    # Week ends on Saturday, get next Saturday at end of day.
    end = start + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59,
                                     milliseconds=999)
    return start, end


def work_periods(records):
    """Get timedeltas during which status was clocked in."""
    timedeltas = []
    records_iter = iter(records)
    for record in records_iter:
        if record.event == 'IN':
            end_record = next(records_iter)
            assert end_record.event == 'OUT'
            assert record.project == end_record.project
            duration = end_record.datetime - record.datetime
            in_record = WorkPeriod(start=record.datetime, duration=duration,
                                   project=record.project)
            timedeltas.append(in_record)
    return timedeltas


def report(start=None, end=None):
    """Return a report of clocked in time per project for a given time period.

    By default, returns the report for the past week.

    """
    if not start and not end:
        date = datetime.date.today() - datetime.timedelta(7)
        start, end = get_week_boundaries(date)
    timedeltas = work_periods(get_records(start=start, end=end))
    projects = set([delta.project for delta in timedeltas])

    column_names = ['Project', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Total']
    rows_dict = {proj: [proj] + [0 for _ in range(8)] for proj in projects}

    for delta in timedeltas:
        weekday = delta.start.weekday()
        total_hours = delta.duration.total_seconds() / 3600
        rows_dict[delta.project][(weekday + 1) % 7 + 1] += total_hours
        rows_dict[delta.project][-1] += total_hours
    return column_names, rows_dict.values()


def clock_in(args):
    """Record a clock in event in the clocker file."""
    if is_clocked_in():
        print('aleady clocked in', file=sys.stderr)
        return
    project = args.project or 'default'
    print('clocking in project {}'.format(project))
    now = datetime.datetime.now()
    with open(get_clocker_filename(), 'a') as clocker_file:
        clocker_file.write('{},IN,{}\n'.format(now, project))


def clock_out(args):
    """Record a clock out event in the clocker file."""
    if not is_clocked_in():
        print('not clocked in', file=sys.stderr)
        return
    last_record = get_last_record()
    print('clocking out of project {}'.format(last_record.project))
    now = datetime.datetime.now()
    with open(get_clocker_filename(), 'a') as clocker_file:
        clocker_file.write('{},OUT,{}\n'.format(now, last_record.project))


def print_report(args):
    """Pretty print a report for the given week."""
    date = datetime.datetime.now().date() + 7 * datetime.timedelta(args.week)
    start, end = get_week_boundaries(date)
    print('Report from {} to {}'.format(start.date(), end.date()))
    column_names, project_times = report(start, end)
    header_formats = ['{:<10s}'] + 8 * ['{:>10s}']
    formats = ['{:<10s}'] + 8 * ['{:>10.2f}']
    for header, fmt in zip(column_names, header_formats):
        print(fmt.format(header), end='')
    print()

    for row in project_times:
        for element, fmt in zip(row, formats):
            print(fmt.format(element), end='')
        print()


def main():
    """Parse command line arguments and run appropriate function."""
    parser = argparse.ArgumentParser(description='Simplistic time tracking')
    subparsers = parser.add_subparsers(required=True, dest='command')
    in_parser = subparsers.add_parser(
        'in', help='Clock in the desired project')
    in_parser.add_argument(
        'project', help='Project name', nargs='?', default=None)
    in_parser.set_defaults(func=clock_in)
    out_parser = subparsers.add_parser(
        'out', help='Clock in the desired project')
    out_parser.set_defaults(func=clock_out)
    report_parser = subparsers.add_parser(
        'report', help='Clock in the desired project')
    report_parser.add_argument(
        'week', nargs='?', default=-1, type=int,
        help='Week number relative to current week (default is -1, previous week)')
    report_parser.set_defaults(func=print_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
