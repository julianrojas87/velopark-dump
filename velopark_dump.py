import sys
import urllib.request
import urllib.parse
import ast
import rdflib
import csv

def test_encode():
    #basic tests
    test_single_encode([("SingleTest","http://schema.org/Monday","00:00:00","01:00:00")],"Mon_00:00-01:00")
    test_single_encode([("WrongOrderTest","http://schema.org/Monday","20:00:00","01:00:00")],"Mon_01:00-20:00")
    test_single_encode([("TestComplexDay","http://schema.org/Monday","00:00:00","01:00:00"),("TestComplexDay","http://schema.org/Monday","10:00:00","11:00:00")],"Mon_00:00-01:00&10:00-11:00")

    #testing days
    test_single_encode([("TestDays","http://schema.org/Monday","00:00:00","01:00:00"),("TestDays","http://schema.org/Sunday","00:05:00","20:31:00")],"Mon_00:00-01:00;Sun_00:05-20:31")
    test_single_encode([("TestEqualDays","http://schema.org/Monday","00:00:00","01:00:00"),("TestEqualDays","http://schema.org/Monday","00:00:00","01:00:00")],"Mon_00:00-01:00")
    test_single_encode([("TestOverlap","http://schema.org/Monday","00:00:00","01:00:00"),("TestOverlap","http://schema.org/Monday","00:30:00","20:00:00")],"Mon_00:00-20:00")
    test_single_encode([("TestTouch","http://schema.org/Monday","00:00:00","01:00:00"),("TestTouch","http://schema.org/Monday","01:00:00","20:00:00")],"Mon_00:00-20:00")
    test_single_encode([("TestCapsule","http://schema.org/Monday","00:00:00","20:00:00"),("TestCapsule","http://schema.org/Monday","00:30:00","10:00:00")],"Mon_00:00-20:00")
    test_single_encode([("TestCapsuleRev","http://schema.org/Monday","00:30:00","10:00:00"),("TestCapsuleRev","http://schema.org/Monday","00:00:00","20:00:00")],"Mon_00:00-20:00")
    test_single_encode([("TestConnect","http://schema.org/Monday","00:00:00","10:00:00"),("TestConnect","http://schema.org/Monday","15:00:00","20:00:00"),("TestConnect","http://schema.org/Monday","10:00:00","15:00:00")],"Mon_00:00-20:00")
    test_single_encode([("TestComplexDays","http://schema.org/Monday","05:00:00","10:00:00"),
                        ("TestComplexDays","http://schema.org/Monday","15:00:00","20:00:00"),
                        ("TestComplexDays","http://schema.org/Monday","00:00:00","01:00:00"),
                        ("TestComplexDays","http://schema.org/Monday","20:30:00","23:00:00"),
                        ("TestComplexDays","http://schema.org/Monday","10:00:00","15:00:00")],"Mon_00:00-01:00&05:00-20:00&20:30-23:00")

    #testing sections
    test_single_encode([("TestSections","http://schema.org/Monday","00:00:00","01:00:00"),("TestSections2","http://schema.org/Sunday","00:05:00","20:31:00")],"Mon_00:00-01:00|Sun_00:05-20:31")
    test_single_encode([("TestEqualSections","http://schema.org/Monday","00:00:00","01:00:00"),("TestEqualSections2","http://schema.org/Monday","00:00:00","01:00:00")],"Mon_00:00-01:00|Mon_00:00-01:00")


def test_single_encode(data,test):
    print("--------")
    print(data[0][0])
    output = get_encoded_hours(data)
    if output == test:
        print("test passed")
    else:
        print("     ==========     ASSERTION FAILED     ==========     ")
        print("expected output: "+test)
        print("actual output:   "+output)

def get_as_list(url):
    return ast.literal_eval(urllib.request.urlopen(url).read().decode())

def query_graph(graph):
    return graph.query(
        """PREFIX schema: <http://schema.org/>
       PREFIX mv: <http://schema.mobivoc.org/>
       PREFIX gr: <http://purl.org/goodrelations/v1#>

       SELECT ?parking ?name ?owner ?address ?postCode ?email ?telephone ?section ?type ?capacity ?numberOfLevels ?covered ?website ?publicAccess ?temporarilyClosed ?intendedAudience ?osm ?latitude ?longitude ?shape ?freeOfCharge ?price
       WHERE {
        ?parking schema:name ?name ;
            mv:ownedBy [ gr:legalName ?owner ] ;
            schema:address [ schema:streetAddress ?address ] ; 
            schema:hasMap [ schema:url ?osm ] .
        OPTIONAL { ?parking schema:address [ schema:postalCode ?postCode ] }
        OPTIONAL {
            ?parking schema:contactPoint [
                    schema:email ?email ;
                    schema:telephone ?telephone
            ] .
        }
        OPTIONAL { ?parking vp:temporarilyClosed ?temporarilyClosed }
        OPTIONAL { ?parking schema:interactionService [ schema:url ?website ] }
        
        GRAPH ?g {
            ?section a ?type ;
                schema:geo [
                    a schema:GeoCoordinates ;
                    schema:latitude ?latitude ;
                    schema:longitude ?longitude
                ] .
                OPTIONAL {
                    ?section mv:totalCapacity ?capacity
                }
                OPTIONAL {
                    ?section schema:publicAccess ?publicAccess
                }
                OPTIONAL {
                    ?section mv:numberOfLevels ?numberOfLevels
                }
                OPTIONAL {
                    ?section vp:covered ?covered
                }
                OPTIONAL {
                    ?section vp:intendedAudience ?intendedAudience
                }
                OPTIONAL {
                    ?x schema:geo [
                        a schema:GeoShape ;
                        schema:polygon ?shape
                    ]
                }
                OPTIONAL {
                    ?section schema:priceSpecification [
                        mv:freeOfCharge ?freeOfCharge
                    ]
                }
                OPTIONAL {
                    ?section schema:priceSpecification [
                        schema:price ?price
                    ]
                }        
        }
        
       }""")

def query_opening(graph):
    return graph.query(
        """PREFIX schema: <http://schema.org/>
        SELECT ?section ?day ?open ?close
        WHERE {
            GRAPH ?g {
                ?section schema:openingHoursSpecification [
                    schema:dayOfWeek ?day;
                    schema:opens ?open;
                    schema:closes ?close
                ]
            }
        }
        """
    )


#encoding the opening hours
#format:   section1|section2...
# section = weekday1;weekday2...
# weekday = dayname_period1&period2...
# period  = start-end

#I also chose to concatenate overlapping periods on the same section and the same day
# ex. Mon_00:00-10:00&05:00-20:00 now becomes Mon_00:00-20:00
#I chose to do this because it adds ease to work with (less data to process) for the user, readability and compactness of the result
# without reducing the correctness of the data or the freedom of the analysis of the data.
def get_encoded_hours(hours):
    #coded_hours = {section1: {weekday1:[(open,close)]}}
    coded_hours = {}
    for hour in hours:
        dayname = hour[1].rsplit('/', 1)[-1][0:3]
        if hour[0] not in coded_hours:
            coded_hours[hour[0]] = {}
        if dayname not in coded_hours[hour[0]]:
            coded_hours[hour[0]][dayname] = []
        #the new period we are trying to insert
        to_place = sorted((hour[2][:-3],hour[3][:-3]))
        start = to_place[0]
        end = to_place[1]
        index = 0
        #in this loop, we try to merge our new period with all overlapping periods
        while index < len(coded_hours[hour[0]][dayname]):
            indexed = coded_hours[hour[0]][dayname][index]
            # this if checks if the current period is overlapping with the new period
            if not (to_place[0] < indexed[0] and to_place[1] < indexed[0] or to_place[0] > indexed[1] and to_place[1] >
                    indexed[1]):
                del coded_hours[hour[0]][dayname][index]
                start = min(start,indexed[0])
                end = max(end,indexed[1])
            else:
                index+=1
        #this adds the new merged period to the periods
        coded_hours[hour[0]][dayname].append((start,end))
    #this is the encoding itself
    return "|".join(
        map(
            lambda section:";".join(
                map(
                    lambda day: day+"_"+"&".join(
                        sorted(map(
                            lambda hour: f"{hour[0]}-{hour[1]}",
                            section[day])
                    )),
                    section.keys())
            ),
            coded_hours.values())
    )

def get_total_capacity(data):
    capacity = 0
    sections = set()
    for row in data:
        if not list(row)[7] in sections:
            sections.add(list(row)[7])
            if(list(row)[9] is not None):
                capacity += int(list(row)[9])
    if capacity > 0:
        return capacity
    else:
        return ""

def testURLS(*codes):
    return [f"https://velopark.ilabt.imec.be/data/NMBS_{code}" for code in codes]


################ Main script logic #################
args = ast.literal_eval(str(sys.argv))
region = args[1]
data_list = []

# possible encode testing
#test_encode()

# get list of parkings
parking_uris = get_as_list("https://velopark.ilabt.imec.be/rich-snippets-generator/api/" + region)
#parking_uris = testURLS(45,94,785,123,689,741,201,656)

for p in parking_uris:
    print("--------------------------------------------")
    p_uri = urllib.parse.urlparse(p)
    print("getting data of parking: " , p_uri.geturl())
    # create a Graph
    g = rdflib.ConjunctiveGraph()
    # parse an RDF file hosted on the Web
    g.default_context.parse(p_uri.scheme + "://" + p_uri.netloc + "/" + urllib.parse.quote(p_uri.path))
    # extract data from graph with a SPARQL query
    data = list(query_graph(g))
    # calculate capacity considering parkings with multiple sections
    capacity = get_total_capacity(data)
    # encode the opening hours to get them in one cell
    hours = list(query_opening(g))
    encoded_hours = get_encoded_hours(hours)
    # organize data for CSV parsing
    relevant_row = list(data[0])
    relevant_row[9] = capacity
    relevant_row.pop(7)
    relevant_row.append(encoded_hours)
    data_list.append(relevant_row)

with open("velopark_" + region + ".csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["parking", "name", "owner", "address", "postCode", "email",
                     "telephone", "type", "capacity", "numberOfLevels", "covered", "website", "publicAccess",
                     "temporarilyClosed", "intendedAudience", "OpenStreetMap", "latitude",
                     "longitude", "shape", "freeOfCharge", "price","openingHours"])
    for row in data_list:
        writer.writerow(row)