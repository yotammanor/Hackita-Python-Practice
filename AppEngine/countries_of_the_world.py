# encoding: utf-8
__author__ = 'yotam'

from sys import path

path.append('lib')

from bottle import route, run, default_app
from geopy import Point
import geopy.distance as Distance
from csv import DictReader
import numpy as Numpy


dict_of_continents = {'SA': 'South America',
                      'NA': 'North America',
                      'AF': 'Africa',
                      'AS': 'Asia',
                      'EU': 'Europe',
                      'AN': 'Antarctica',
                      'OC': 'Oceania'}

detailed_countries_file = open('cow.csv', 'r')
reader = DictReader(detailed_countries_file, delimiter=';')
detailed_countries_list = [row for row in reader]
country_data = {}
continent_set = set()
for country in detailed_countries_list:
    country_details = {'Name': country['ISOen_name'].strip(),
                       'Continent': dict_of_continents[country['continent'].strip()],
                       'Location': Point(latitude=country['latitude'],
                                         longitude=country['longitude']),
                       'Language': country['language']}

    country_data[country['ISOen_name'].strip().lower()] = country_details
    continent_set.add(country_details['Continent'])


def eval_distance(country_origin, country_target):
    distance_between_countries = Distance.distance(country_origin['Location'],
                                                   country_target['Location']).km
    return distance_between_countries


@route('/')
def main():
    #list_of_countries = [x for x in countries_dict.keys()]
    #list_of_countries.sort()
    #list_of_countries_for_html = ['<a href="/country/%s">%s</a>' % (x, x.capitalize())
    #                              for x in list_of_countries]
    #str_of_countries = '<br>'.join(list_of_countries_for_html)

    list_of_continents = [x.lower() for x in continent_set]
    list_of_continents.sort()
    str_of_continents = '<br>'.join(['<a href="/%s">%s</a>' % (x, x.capitalize())
                                     for x in list_of_continents])

    return '%s' % str_of_continents


@route('/<continent>')
def display_countries_in_continent(continent):

    list_of_names = [country_info['Name'].lower() for country_key, country_info
                     in country_data.items() if country_info['Continent'].lower() == continent]
    list_of_names.sort()
    list_of_names = ['<a href="/country/%s">%s</a>' % (x.lower(), x.capitalize())
                     for x in list_of_names]
    str_of_names = '<br>'.join(list_of_names)
    return '%s <br><br> <a href="/">List Of Continents</a>' % str_of_names


@route('/country/<country_name>')
def display_country_info(country_name):

    country_for_display = country_data[country_name]
    countries_dict_for_country_in_display = country_data
    for country_key, country_value in countries_dict_for_country_in_display.items():
        countries_dict_for_country_in_display[country_key]['dist_from_origin'] = \
            eval_distance(country_for_display, country_value)

    list_of_names = [x for x in countries_dict_for_country_in_display.keys()]
    list_of_names.sort()
    list_of_distances = [(countries_dict_for_country_in_display[country_name]['dist_from_origin'])
                         for country_name in list_of_names]

    order_of_distances = Numpy.argsort(list_of_distances)

    ordered_list_of_names = [list_of_names[x] for x in order_of_distances]

    list_of_close_country_html = []
    for i, country_name in enumerate(ordered_list_of_names[1:6]):
        html_close_country = '%d. <a href="/country/%s">%s</a> - %s KM ' % \
                             (i+1, country_name,  country_name,
                              '{0:.2f}'.format(countries_dict_for_country_in_display[country_name]['dist_from_origin']))
        list_of_close_country_html.append(html_close_country)
    html_of_top_5_closest_countries = '<br>'.join(list_of_close_country_html)
    return 'this is %s <br><br> %s  <br><br> \
    Top 5 closest countries:<br> %s <br><br> \
    <a href="/%s">Back to continent </a><br><br>\
     <a href="/">List Of Continents</a> ' % (country_for_display['Name'], country_for_display,
                                             html_of_top_5_closest_countries,
                                             country_for_display['Continent'].lower())

application = default_app()

if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True, reloader=True)
