import argparse
import os
from astro_charts.chart_creator import ChartCreator
from dotenv import load_dotenv
import json
from astro_charts.magi_linkages import MagiLinkageCalculator
from astro_charts.kerykeion_chart import KerykeionChartSVG
from kerykeion.astrological_subject import AstrologicalSubject
from astro_charts.magi_synastry import MagiSynastryCalculator
from astro_charts.services.geo_service import GeoService
from timezonefinder import TimezoneFinder
import sys

load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description="Generate astrological charts.")
    
    # Required arguments for all chart types
    parser.add_argument('--name', required=True, help="Name of the person")
    parser.add_argument('--year', type=int, required=True, help="Birth year")
    parser.add_argument('--month', type=int, required=True, help="Birth month")
    parser.add_argument('--day', type=int, required=True, help="Birth day")
    parser.add_argument('--hour', type=int, required=True, help="Birth hour")
    parser.add_argument('--minute', type=int, required=True, help="Birth minute")
    parser.add_argument('--city', required=True, help="Birth city")
    parser.add_argument('--nation', required=True, help="Birth nation")
    
    # Optional arguments
    parser.add_argument('--output', help="Output file name")
    parser.add_argument('--type', choices=['natal', 'transit', 'synastry'], 
                       required=True, help="Type of chart to generate")
    
    # Transit date arguments (optional, defaults to current date/time)
    parser.add_argument('--transit-year', type=int, help="Transit year")
    parser.add_argument('--transit-month', type=int, help="Transit month")
    parser.add_argument('--transit-day', type=int, help="Transit day")
    parser.add_argument('--transit-hour', type=int, help="Transit hour")
    parser.add_argument('--transit-minute', type=int, help="Transit minute")
    
    # Synastry arguments
    parser.add_argument('--name2', help="Name of the second person (for synastry)")
    parser.add_argument('--year2', type=int, help="Birth year of second person")
    parser.add_argument('--month2', type=int, help="Birth month of second person")
    parser.add_argument('--day2', type=int, help="Birth day of second person")
    parser.add_argument('--hour2', type=int, help="Birth hour of second person")
    parser.add_argument('--minute2', type=int, help="Birth minute of second person")
    parser.add_argument('--city2', help="Birth city of second person")
    parser.add_argument('--nation2', help="Birth nation of second person")

    return parser.parse_args()

def print_chart_data(data, chart_type):
    """Print formatted chart data based on chart type"""
    print("\nChart Data:")
    print("===========")

    try:
        if chart_type == 'synastry':
            # Print Person 1 data
            print(f"\nPerson 1 ({data['person1']['subject']['name']}):")
            print(f"Birth Date: {data['person1']['subject']['birth_data']['date']}")
            print(f"Birth Time: {data['person1']['subject']['birth_data']['time']}")
            print(f"Location: {data['person1']['subject']['birth_data']['location']}")
            
            # Print Person 2 data
            print(f"\nPerson 2 ({data['person2']['subject']['name']}):")
            print(f"Birth Date: {data['person2']['subject']['birth_data']['date']}")
            print(f"Birth Time: {data['person2']['subject']['birth_data']['time']}")
            print(f"Location: {data['person2']['subject']['birth_data']['location']}")
            
            # Print Saturn Clashes
            if data.get('saturn_clashes'):
                print("\nSaturn Clashes:")
                for clash in data['saturn_clashes']:
                    print(f"{clash['saturn_person']}'s Saturn {clash['aspect_name']} to")
                    print(f"{clash['planet_person']}'s {clash['planet2_name'].title()}")
                    print(f"Aspect: {clash['aspect_degrees']}° (orb: {round(clash['orbit'], 2)}°)")
                    print()
            else:
                print("\nNo Saturn Clashes found")

            # Print Cinderella Linkages
            if data.get('cinderella_linkages'):
                print("\nCinderella Linkages:")
                for linkage in data['cinderella_linkages']:
                    print(f"{linkage['person1_name']}'s {linkage['planet1_name'].title()} {linkage['aspect_name']} to")
                    print(f"{linkage['person2_name']}'s {linkage['planet2_name'].title()}")
                    print(f"Aspect: {linkage['aspect_degrees']}° (orb: {round(linkage['orbit'], 2)}°)")
                    print()
            else:
                print("\nNo Cinderella Linkages found")
            
            print(f"\nChart saved to: {data['chart_path']}")

            # Print full JSON data
            print("\nFull JSON Data:")
            print("===============")
            print(json.dumps(data, indent=2))

        elif chart_type == 'transit':
            # ... existing transit printing code ...
            # Print full JSON data
            print("\nFull JSON Data:")
            print("===============")
            print(json.dumps(data, indent=2))

        elif chart_type == 'natal':
            # ... existing natal printing code ...
            # Print full JSON data
            print("\nFull JSON Data:")
            print("===============")
            print(json.dumps(data, indent=2))
            
    except KeyError as e:
        print(f"Error accessing data structure: {str(e)}")
        print("Raw data structure:", json.dumps(data, indent=2))

def main():
    try:
        args = parse_args()
        
        # Initialize chart creator
        chart_creator = ChartCreator(
            name=args.name,
            year=args.year,
            month=args.month,
            day=args.day,
            hour=args.hour,
            minute=args.minute,
            city=args.city,
            nation=args.nation
        )

        # Generate chart data based on type
        if args.type == 'natal':
            chart_data = chart_creator.get_chart_data_as_json()
        elif args.type == 'transit':
            chart_data = chart_creator.create_transit_chart(
                transit_year=args.transit_year,
                transit_month=args.transit_month,
                transit_day=args.transit_day,
                transit_hour=args.transit_hour,
                transit_minute=args.transit_minute
            )
        elif args.type == 'synastry':
            chart_data = chart_creator.create_synastry_chart(
                name2=args.name2,
                year2=args.year2,
                month2=args.month2,
                day2=args.day2,
                hour2=args.hour2,
                minute2=args.minute2,
                city2=args.city2,
                nation2=args.nation2
            )

        # Parse and print the data
        data = json.loads(chart_data)
        print_chart_data(data, args.type)

        # Save to file if output specified
        if args.output:
            with open(args.output, 'w') as f:
                f.write(chart_data)
            print(f"\nFull chart data saved to {args.output}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()