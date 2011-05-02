#!/usr/bin/env python

import os, re, sha, shelve, charts
from colour import *
from utils import *
from fastcgi import *

location_names = {'1601 ALLSTON WAY': 'The Convent',
                  '1730 LA LOMA AVE': 'Kingman Hall',
                  '1777 EUCLID AVE': 'Euclid Hall',
                  '2250 PROSPECT ST': 'Sherman Hall',
                  '2311 WARRING ST': 'Andres Castro Arms',
                  '2347 PROSPECT ST': 'African American Theme House',
                  '2405 PROSPECT ST': 'Lothlorien Hall', # north house?
                  '2410 WARRING ST': 'Oscar Wilde House',
                  '2415 DWIGHT WAY': '2415 Dwight Way (unknown)',
                  '2415 PROSPECT ST': 'Lothlorien Hall', # south house?
                  '2419 DWIGHT WAY': 'Fenwick Weavers\' Village?',
                  '2424 RIDGE RD': 'Casa Zimbabwe?',
                  '2424 RIDGE RD REAR': 'Central Office?',
                  '2519 RIDGE RD RM HSE': 'Hoyt Hall',
                  '2527 RIDGE RD RM HSE': 'Stebbins Hall',
                  '2539 HILLEGASS AVE': 'Hillegass Parker House?', # neighbour?
                  '2540 LE CONTE AVE': 'Northside Apartments?', # also 2526
                  '2545 HILLEGASS AVE': 'Hillegass Parker House?', # north?
                  '2562 LE CONTE AVE': 'Kidd Hall',
                  '2600 RIDGE RD': 'Cloyne Court',
                  '2601 PARKER ST LOWR': 'Hillegass Parker House?', # south?
                  '2601 PARKER ST REAR ES': 'Hillegass Parker House?', # south?
                  '2601 PARKER ST UPPR WS': 'Hillegass Parker House?', # south?
                  '2732 DURANT AVE': 'Wolf House',
                  '2826 8TH ST': '2826 8th St. (unknown)',
                  '2833 BANCROFT WY': 'Davis House'}

location_occupants = {'The Convent': 25,
                      'Kingman Hall': 50,
                      'Euclid Hall': 24,
                      'Sherman Hall': 40,
                      'Andres Castro Arms': 56,
                      'African American Theme House': 21,
                      'Lothlorien Hall': 57,
                      'Oscar Wilde House': 38,
                      'Fenwick Weavers\' Village?': 102,
                      'Casa Zimbabwe?': 124,
                      'Hoyt Hall': 60,
                      'Stebbins Hall': 62,
                      'Hillegass Parker House?': 57,
                      'Northside Apartments?': 26,
                      'Kidd Hall': 17,
                      'Cloyne Court': 148,
                      'Wolf House': 28,
                      'Davis House': 36,
                      'Central Office?': 10,
                      '2415 Dwight Way (unknown)': 10,
                      '2826 8th St. (unknown)': 10}


# missing:
# Casa Zimbabwe (2422 Ridge)
# Ridge (2420 Ridge)
# Castro (2310 Prospect)
# Rochdale (2424 Haste)
# Fenwick (2415 Dwight) - usage at 2419 Dwight is zero
# Central Office has no electricity usage
# Northside usage seems too small

# extra:
# 2311 Warring (Castro?)
# 2415 Prospect (Loth south house?)
# 2419 Dwight
# 2539 Hillegass (next door to HiP house?)
# 2601 Parker (HiP south house?)
# 2826 8th St (what the heck is this?)

def date_range(start, end):
    """Return all dates between start and end, inclusive."""
    date = start
    while date <= end:
        yield date
        date += 1

def month_range((y, l)):
    """Return all dates in the given month."""
    date = Date(y, l, 1)
    while date.month == l:
        yield date
        date += 1

def most_frequent_item(list):
    """Return the most frequently occurring item in the given list."""
    counts = {}
    for item in list:
        counts[item] = counts.get(item, 0) + 1
    return max(counts.items(), key=lambda (item, count): count)[0]

def month(date):
    """Get the (year, month) pair from a Date object."""
    y, l, d = date.yld()
    return (y, l)

def approx_month(start, end):
    """Find the month that the given date range mostly covers."""
    sy, sl, sd = start.yld()
    ey, el, ed = end.yld()
    if (sy, sl) == (ey, el):
        return (sy, sl)
    if sy*12 + sl + 1 == ey*12 + el:
        last_day = Date(ey, el, 1) - 1
        start_days = last_day.day + 1 - sd
        if start_days > ed:
            return (sy, sl)
        else:
            return (ey, el)
    if sy*12 + sl + 2 == ey*12 + el:
        if sl < 12:
            return (sy, sl + 1)
        else:
            return (sy + 1, 1)
    return most_frequent_item(month(date) for date in date_range(start, end))

def fix_key(key):
    key = key.strip('_')
    return {'electric_charges': 'charges',
            'electric_usage': 'usage',
            'gas_charges': 'charges',
            'gas_usage': 'usage'}.get(key, key)

def sum_intervals(intervals, key='usage'):
    """Spread the usage (or charges) of each interval over the days in the
    interval, producing totals for each day."""
    days = {}
    for interval in intervals:
        daily_value = float(interval[key])/interval['days']
        for date in date_range(interval['from'], interval['to']):
            days[date] = days.get(date, 0) + daily_value
    return days

def daily_average(day_values, dates):
    """Get the average value for each day in the given list of dates."""
    count, total = 0, 0.0
    for date in dates:
        if date in day_values:
            count += 1
            total += day_values[date]
    if count == 0:
        return 0.0
    return total/count

def parse_records(text):
    """Parse the contents of a text file into energy usage records."""
    service_profiles = {}
    service_intervals = {}
    service_id = None
    for line in text.split('\n'):
        # Get non-empty records.
        if line.strip().startswith('#') or not line.strip():
            continue
        record = dict((fix_key(k), v) for (k, v) in
                      eval('dict(' + line + ')').items())

        # Starting a series of records about a new service ID?
        if 'service_id_number' in record:
            service_id = record['service_id_number']
            service_profiles.setdefault(service_id, {})
            service_intervals.setdefault(service_id, [])

        # Detect and clean up dates.
        for key, value in record.items():
            if isinstance(value, basestring):
                try:
                    record[key] = parse_date(value)
                except ValueError:
                    pass

        if service_id:
            if 'from' in record:
                # Store service interval records.
                record['service_id'] = service_id
                record['month'] = approx_month(record['from'], record['to'])
                service_intervals[service_id].append(record)
            else:
                # Store service profile records.
                if record['rate_schedule'].startswith('Gas'):
                    record['type'] = 'gas'
                if record['rate_schedule'].startswith('Elec'):
                    record['type'] = 'electricity'
                service_profiles[service_id].update(record)

    # Organize the records by location and type.
    services = {}
    for service_id, profile in service_profiles.items():
        address = profile['address']
        location = location_names.get(address, address)
        location = address + ' ' + str(service_id)
        if address in location_names:
            location += ' (%s)' % location_names[address]
        type = profile['type']
        profiles, intervals = services.setdefault((location, type), ([], []))
        profiles.append(profile)
        intervals.extend(service_intervals[service_id])
        intervals.sort(key=lambda record: record['from'])
    return services

def prepare_data(services):
    """Prepare the data for the summary chart."""

    # Determine the last month to display by looking for the month that
    # most of the services have as their last month.
    last_months = []
    for location, type in services:
        profiles, intervals = services[location, type]
        if intervals:
            last_months.append(intervals[-1]['month'])
    y, l = last_month = most_frequent_item(last_months)

    # Get data to chart for the two years prior to this month.
    last = y*12 + (l - 1)
    months = [(int(m/12), (m % 12) + 1) for m in range(last - 23, last + 1)]

    # Gather the data to chart and the last-month value for each service.
    history_data = {}
    last_month_usage = {}
    for location, type in services:
        profiles, intervals = services[location, type]
        occupants = 20 # float(location_occupants[location])
        daily_totals = sum_intervals(intervals)
        history_data[location, type] = [
            daily_average(daily_totals, month_range(month))/occupants
            for month in months]

    return last_month, history_data

def load(filename, cache_filename):
    """Load and process energy usage records from a text file."""
    cache = shelve.open(cache_filename, 'c')
    text = open(filename).read()
    digest = sha.sha(text).hexdigest()
    if digest not in cache:
        services = parse_records(text)
        last_month, history_data = prepare_data(services)
        cache[digest] = services, last_month, history_data
        cache.sync()
    return cache[digest]

services, last_month, history_data = load('energy.txt', 'energy.cache')

if form.location in services and form.type in services[form.location]:
    # Show details about a particular service at a particular location.
    prologue('Kingman Hall: Energy Consumption', 'style.css')
    write(h1(esc(form.type.capitalize()), ' usage for ',
             esc(form.location)))
    epilogue()

elif form.location:
    prologue('Kingman Hall: Energy Consumption', 'style.css')
    write(h1('No records found'), p,
             'There are no ', esc(form.type),
             ' usage records for ', esc(form.location), '.')
    epilogue()

else:
    # Generate the cells for the table.
    y, l = last_month
    formatted_month = Date(y, l, 1).format('%mmm %yy')
    DUP = 30  # Turn each data point into 30 points to make a bar
    stops = [(12-l)*DUP - 0.5, (24-l)*DUP - 0.5]
    # stops = [11.5 - l, 23.5 - l]
    rows = [tr(th('Location'), # th('Occupants'),
               th('Average daily usage per occupant', colspan=4), c='head'),
            tr(td(),
               th('Electricity', c='electricity'),
               th(formatted_month, c='electricity last-month'),
               th('Natural Gas', c='gas'),
               th(formatted_month, c='gas last-month'))]
    locations = sorted(set(location_names.values()))
    locations = sorted(set([location for (location, type) in services]))
    id = 0
    for location in locations:
        id += 1
        hover = {'onmouseover': "highlight('row%d', 1)" % id,
                 'onmouseout': "highlight('row%d', 0)" % id}
        addresses = ', '.join(sorted(
            key for key in location_names if location_names[key] == location))
        occupants = '(%d occupants)' % location_occupants.get(location, 20)
        row = td(location, div(addresses, ' ', occupants, c='details'),
                 c='location', **hover)
        for type, unit, limit, colour in [
            ('electricity', 'kWh', 20, Colour(0.2, 0.6, 0.0)),
            ('gas', 'th', 2, Colour(0.4, 0.0, 1.0))]:
            if (location, type) not in history_data:
                row += [td(**hover), td(**hover)]
                continue
            url = 'energy.cgi?' + form_encode(location=location, type=type)
            data = sum([[x]*DUP for x in history_data[location, type]], [])
            # data = history_data[location, type]
            sparkline = charts.sparkline(150, 24, data, limit, colour, 1, stops)
            row += td(a(img(sparkline), href=url), **hover)
            row += td('%.2f %s' % (data[-1], unit),
                      c=type + ' last-month', **hover)
        rows.append(tr(row, id='row%d' % id))

    prologue('Kingman Hall: Energy Consumption', 'style.css')
    write_template('energy.html', table=table(rows, c='summary'))
    epilogue()
