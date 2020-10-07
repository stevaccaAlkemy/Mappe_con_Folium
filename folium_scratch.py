import os
import pandas as pd
from branca.element import Template, MacroElement
import branca

import folium
from folium.plugins import MeasureControl
from folium import *
from folium.plugins import TimestampedGeoJson
from folium import plugins
from functools import partial
from geopy.geocoders import Nominatim


def define_legend(dataframe, names, topic_names, title):
    """
    Function to build the legend
    :param dataframe: pandas dataframes
    :param names: dict with topi labels and colors associated
    :param topic_names: topic names
    :param title:
    :return:
    """

    # (color, Label name, label count)
    topic0 = (names[topic_names[0]], topic_names[0], dataframe[topic_names[0]].sum())
    topic1 = (names[topic_names[1]], topic_names[1], dataframe[topic_names[1]].sum())
    topic2 = (names[topic_names[2]], topic_names[2], dataframe[topic_names[2]].sum())

    return """
    {% macro html(this, kwargs) %}

    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=3">
      <title>""" + title + """</title>
      <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

      <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
      <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

      <script>
        $( function() {
            $( "#maplegend" ).draggable({
                start: function (event, ui) {
                    $(this).css({
                        right: "auto",
                        top: "auto",
                        bottom: "auto"
                    });
                }
            });
        });
        toggleTopic = (markerClass, topicColor) => {
            var elements = document.querySelectorAll(".leaflet-interactive")
            console.log("elements", elements);
            if(elements){
                for(key in elements){
                    if(elements[key] && elements[key].getAttribute && elements[key].getAttribute("stroke") == topicColor)
                            elements[key].classList.toggle("disabled-marker");
                }
            }
            var topic = document.getElementById("topic-" + topicColor);
            if(topic){
                topic.classList.toggle("disabled-topic");
            } 
        }

      </script>
      <style>
        .awesome-marker-icon-green{
            display: none;
        }
      </style>
    </head>
    <body>


    <div id='maplegend' class='maplegend' 
        style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
         border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>

    <div class='legend-title'>Map Legend </div>
    <div class='legend-scale'>
      <ul class='legend-labels'>
        <li><span style='background:""" + topic0[0] + """;opacity:0.8;'>
        </span>""" + topic0[1] + " &#8594 " + str(topic0[2]) + """ tweet</li>
        <li><span style='background:""" + topic1[0] + """;opacity:0.8;'>
        </span>""" + topic1[1] + " &#8594 " + str(topic1[2]) + """ tweet</li>
        <li><span style='background:""" + topic2[0] + """;opacity:0.8;'>
        </span>""" + topic2[1] + " &#8594 " + str(topic2[2]) + """ tweet</li>

        <body>

          <fieldset><legend style="font-size:9px"><br> Tweet estratti dal 12 al 19 Giugno 2020 con chiavi <br>
          di ricerca #coronavirus OR #covid19 OR <br>#coronavirusitalia grazie all'utilizzo di Twitter API</legend></fieldset>
        </body>

      </ul>
    </div>
    </div>

    </body>
    </html>

    <style type='text/css'>
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 1px solid #999;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    <style>
        * {
            font-family: Open Sans;
            color: #2e3c43;
        }
        .sidebar{
            position: absolute;
            top: 0;
            right: 0;
            height: 100vh;
            width: 350px;
            background: white;
            z-index: 999;
        }
        
        #maplegend {
            background: white !important;
            top: 5px !important;
            left: 5px !important;
            right: auto !important;
            bottom: auto !important;
        }
        .disabled-marker{
            opacity: 0 !important;
        }
        .first-row{
            display: flex;
            flex-direction: row;
            margin-bottom: 5px;
        }
        .topic-value{
            flex-grow: 1;
            text-align: right;
        }
        
        .second-row, .topic-progress{
            height: 4px;
            border-radius: 4px
        }
        
        .second-row{
            background: #eee;
        }
        .topic-item{
            margin-bottom: 10px;
            cursor: pointer;
        }
        .disabled-topic{
            opacity: 0.3;
        }
        
        .leaflet-interactive{
            opacity: 1;
            transition-property: opacity;
            transition-duration: .1s;
            transition-delay: 0s;
            transition-timing-function: linear;
        }
        
        .leaflet-top.leaflet-right{
            z-index: 888 !important;
        }
        
        #map-legend{
            top: 5px;
            left: 5px;
            pointer-events: none;
        }
        .total-tweet-section{
            padding: 20px 20px;
        }
        .total-tweet-section .title{
            font-size: 18px;
            line-height: 22px;
        }
        .total-tweet-section .counter{
            font-size: 26px;
            line-height: 34px;
        }
        .total-tweet-section .source{
            font-size: 10px;
            line-height: 14px;
        }
        
        .divider{
            background: #F2F6F9;
            height: 3px;
        }
        .topics-container{
            padding: 20px 20px;
        }
        
        .topic-name{
            font-size: 12px;
            line-height: 16px;
            text-transform: uppercase;
            font-weight: 600;
        }
        .topic-value{
            font-size: 10px;
            display: flex;
            align-items: flex-end;
            justify-content: flex-end;
        }
        
        .leaflet-bottom.leaflet-right{
            left: 10px !important;
            right: auto !important;
        }
        
        .leaflet-bottom.leaflet-right .leaflet-control-minimap{
            float: left !important;
        }
        
        .topic-keywords{
            padding: 0 20px;
            margin-bottom: 15px;
        }
        
        .topic-count{
            margin: 5px 0;
            font-size: 26px;
            line-height: 34px;
        }
    </style>
    {% endmacro %}"""


def fancy_html(row):
    left_col_colour = "#4682B4"
    right_col_colour = "#E6E6FA"  # "#C5DCE7"

    html = """<!DOCTYPE html>
                <html>
                <font size="1.8" face="Verdana" >
                    <table style="width: 100%;">
                <tbody>
                <tr>
                <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">Topic label</span></td>
                <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(
        row.topic_label) + """
                </tr>
                <tr>
                <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">User Location </span></td>
                <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(
        row.user_location) + """
                </tr>
                <tr>
                <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">Tweet text</span></td>
                <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(row.text) + """
                </tr>
                <tr>
                <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">Time data </span></td>
                <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(
        row.created_at) + """
                </tr>
                <tr>
                <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">Number of followers</span></td>
                <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(
        row.followers) + """
                </tr>
                <tr>
                <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">Number of retweet </span></td>
                <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(
        row.retweet_count) + """
                </tr>
                <tr>
                <td style="background-color: """ + left_col_colour + """;"><span style="color: #ffffff;">Mentions </span></td>
                <td style="width: 200px;background-color: """ + right_col_colour + """;">{}</td>""".format(
        row.mentions) + """
                </tr>
                </tbody>
                </table>
                </html>
                """
    return html


def render_topic(topic):
    return """
        <div id='topic-%s' class='topic-item' onclick='toggleTopic("%s", "%s")'>
            <div class='first-row'>
                <div class='topic-name'>
                    %s
                </div>
                <div class='topic-value'>
                    %s (%s)
                </div>
            </div>
            <div class='second-row'>
                <div class='topic-progress' style='background-color: %s; width: %s'></div>
            </div>
        </div>
    """ % (topic["background"], topic["color"], topic["background"], topic["name"], topic["value"], topic["progress"], topic["background"], topic["progress"])


from random import randint

def html_topics_container(topic_names):
    resulting_html = []
    resulting_html.append("""<div class='topics-container'>""")
    # marker_colors = ["awesome-marker-icon-red", "awesome-marker-icon-green", "awesome-marker-icon-blue"]
    color_mark = 'awesome-marker-icon-'
    topics = []
    for topic in topic_names:
        t = {
            "name": topic,
            "color": color_mark+names[topic],
            "value": 100,
            "background": names[topic],
            "progress": str(randint(0, 100)) + "%"
        }
        topics.append(t)
    for topic in topics:
        resulting_html.append(render_topic(topic))

    resulting_html.append("""</div>""")
    return resulting_html


def render_topic_keywords(topic):
    return """
        <div id='topic-keywords-%s' class='topic-keywords'>
            <div class='topic-name'>
                %s
            </div>
            <div class='topic-count'>
                %s
            </div>
            <div class='keywords'>
                %s
            </div>
        </div>
    """ % (topic["name"], topic["name"], topic["count"], topic["keywords"])


def html_topics_keywords(topic_names):
    resulting_html = []
    resulting_html.append("""<div class='topics-keywords-container'>""")
    topics = []
    for topic in topic_names:
        t = {
            "name": topic,
            "keywords": topics_keywords[topic],
            "count": randint(0, 100)

        }
        topics.append(t)
    for topic in topics:
        resulting_html.append(render_topic_keywords(topic))

    resulting_html.append("""</div>""")
    return resulting_html



def update_regions(string):
    check = False
    for i in regions:
        refs = []
        refs = regions[i]["refs"].split("/")
        # print(refs)
        for ref in refs:
            if string.lower().find(ref) != -1:
                # print("found")
                check = True
                break
            else:
                check = False
        if check == True:
            regions[i]["count"] = regions[i]["count"] + 1
            break
    if check == False:
        print(string)
        return 1
    else:
        return 0
def folium_map(dataframe, names, title):
    dataframe = dataframe[dataframe['latitude'].notna()]
    dataframe = dataframe[dataframe['longitude'].notna()]
    # print(dataframe.head(2))

    attr = ("""&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, 
                &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors""")
    tiles = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'

    # MAPPA
    m = folium.Map(
        tiles='CartoDB dark_matter',  # 'Cartodb Positron',
        # attr=attr,
        zoom_start=15,
        # world_copy_jump=True,
        # no_wrap=True
    )

    topic_names = list(names.keys())
    # folium.TileLayer('CartoDB dark_matter', name='darktile').add_to(m)

    for i, value in dataframe.iterrows():
        tooltip = 'Click me!'

        html = fancy_html(value)
        iframe = branca.element.IFrame(html=html, width=300, height=180)
        popup = folium.Popup(iframe, parse_html=False)

        folium.Circle((value.latitude, value.longitude),
                      popup=popup,
                      color=names[value.topic_label],
                      fill=names[value.topic_label],
                      radius=5,
                      className="aaa",
                      # icon=icon,
                      region="regione",
                      tooltip=tooltip).add_to(m)

    # folium.LayerControl(collapsed=False).add_to(m)

    # Add custom legend
    macro = MacroElement()
    template = define_legend(dataframe, names, topic_names, title)
    macro._template = Template(template)
    regions_array = []
    regions_not_found = 0

    for i, value in dataframe.iterrows():
        not_found = update_regions(value.user_location)
        regions_not_found += not_found

    for key in regions:
        if regions[key]["count"] > 0:
            regions_array.append(regions[key])
    print(regions_array, len(regions_array))
    print("regions not found", regions_not_found)
    topics_html = ''.join(html_topics_container(topic_names))
    topics_keywords_html = ''.join(html_topics_keywords(topic_names))

    string_html = """
    <div class="sidebar">
      <div class="total-tweet-section">
        <div class="title">%s</div>
        <div class="counter">%s</div>
        <div class="source">%s</div>
      </div>
      <div class="divider"></div>
    %s
    %s
    </div>
    """ % ("Analysis tweets", 28802, "Source: Twitter API", topics_html, topics_keywords_html)

    # print(string_html)
    m.get_root().html.add_child(folium.Element(string_html))

    # macro._template = Template(''.join(html_topics_container(topic_names)))

    m.get_root().add_child(macro)

    m.add_child(MeasureControl())

    plugins.Fullscreen(
        position='topright',
        title='Expand me',
        title_cancel='Exit me',
        force_separate_button=True
    ).add_to(m)

    minimap = plugins.MiniMap()
    m.add_child(minimap)
    print(str(len(df)) + " cluster")
    # mc = plugins.MarkerCluster().add_to(m)
    # n_layer = int(len(df) / 100)
    # total_marker = 0
    # for j in range(n_layer):
    #     layer = folium.map.FeatureGroup()
    #     count = 0
    #     for i, value in dataframe.iterrows():
    #         tooltip = 'Click me!'
    #         count = count + 1
    #         html = fancy_html(value)
    #         iframe = branca.element.IFrame(html=html, width=300, height=180)
    #         popup = folium.Popup(iframe, parse_html=False)
    #         folium.Marker([float(value.latitude), float(value.longitude)],
    #                       popup=popup,
    #                       icon=folium.Icon(color=names[f'{value.topic_label}']),
    #                       # icon=icon,
    #                       tooltip=tooltip).add_to(layer)
    #         if count == 100 or total_marker == len(df) or count == len(df):
    #             break
    #     total_marker += count
    #     m.add_child(layer)
    #     print("total marker", total_marker)
    return m


if __name__ == '__main__':

    # title_map = '7466_Immigrazione e Migranti_nuovo'
    title_map = 'Costruzione_mappa_prova'

    topic0_keywords = "Keywords: 'migrare', 'nave', 'tampone', 'governare', <br>" \
                      "'pago', 'cibare', 'imbarcazione', 'arrivato', 'lingua', <br>" \
                      "'regolamentare', 'rimediare', 'trasferire', 'coronavirus'<br>"
    topic1_keywords = "Keywords: 'morto',  'libia', 'famiglia', 'salute', 'strage',<br>" \
                      "'funerale', 'malta', 'porcata', 'omissione, <br>" \
                      "'tutelare', 'problema'<br>"
    topic2_keywords = "Keywords: 'lavorare', 'bellanova', 'salvini', 'nemico',<br> " \
                      "'straniero', 'parlamentare',  'regolarizzare', <br>" \
                      "'preferire', 'vattene', 'hotel', 'sfruttare'"

    names = {'Covid e sbarco migranti': 'red', 'Migranti: tragedie e decessi': 'green',
             'Regolarizzazione immigrati': 'darkblue'}
    topics_keywords = {'Covid e sbarco migranti': topic0_keywords, 'Migranti: tragedie e decessi': topic1_keywords,
             'Regolarizzazione immigrati': topic2_keywords}

    regions = {
        "abruzzo": {
            "name": "Abruzzo",
            "refs": "abruzzo",
            "count": 0
        },
        "basilicata": {
            "name": "Basilicata",
            "refs": "basilicata",
            "count": 0
        },
        "calabria": {
            "name": "Calabria",
            "refs": "calabria",
            "count": 0
        },
        "campania": {
            "name": "Campania",
            "refs": "campania/napoli/casoria",
            "count": 0
        },
        "emilia-romagna": {
            "name": "Emilia-Romagna",
            "refs": "emilia-romagna/emilia romagna/emilia romagn/castel bolognese/budrio/ravenna/faenza",
            "count": 0
        },
        "friuli-venezia-giulia": {
            "name": "Friuli-Venezia-Giulia",
            "refs": "friuli-venezia-giulia",
            "count": 0
        },
        "lazio": {
            "name": "Lazio",
            "refs": "lazio/roma/viterbo",
            "count": 0
        },
        "liguria": {
            "name": "Liguria",
            "refs": "liguria/andora/genova",
            "count": 0
        },
        "lombardia": {
            "name": "Lombardia",
            "refs": "lombardia/milano/rozzano/gardaland/lonate",
            "count": 0
        },
        "marche": {
            "name": "Marche",
            "refs": "marche/piceno",
            "count": 0
        },
        "molise": {
            "name": "Molise",
            "refs": "molise",
            "count": 0
        },
        "piemonte": {
            "name": "Piemonte",
            "refs": "piemonte/ciriè/torino/cuneo",
            "count": 0
        },
        "puglia": {
            "name": "Puglia",
            "refs": "puglia/bari/gallipoli",
            "count": 0
        },
        "sardegna": {
            "name": "Sardegna",
            "refs": "sardegna/cagliari/sassari/nuoro/oristano/olbia/olbia tempio",
            "count": 0
        },
        "sicilia": {
            "name": "Sicilia",
            "refs": "sicilia/palermo/favara",
            "count": 0
        },
        "toscana": {
            "name": "Toscana",
            "refs": "toscana/firenze/arezzo/livorno",
            "count": 0
        },
        "trentino-alto-adige": {
            "name": "Trentino-Alto-Adige",
            "refs": "trentino-alto-adige/trentino alto adige/trento",
            "count": 0
        },
        "umbria": {
            "name": "Umbria",
            "refs": "umbria/perugia",
            "count": 0
        },
        "valle-da-aosta": {
            "name": "Valle D'Aosta",
            "refs": "valle d'aosta",
            "count": 0
        },
        "veneto": {
            "name": "Veneto",
            "refs": "veneto/venezia",
            "count": 0
        }
    }

    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'refactored_NEW_geo_topic_7466_Immigrazione e Migranti.csv'))
    df = df.drop('Unnamed: 0', axis=1)
    # df = df[5000:5100]

    # geolocator = Nominatim(user_agent="prova")
    # reverse = partial(geolocator.reverse, language="it")
    # results = []
    # for i, value in df.iterrows():
    #     address = reverse("{}, {}".format(str(value["latitude"]), str(value["longitude"])))
    #     results.append(address)
    # df["regione"] = [str(r).split(",")[-3] for r in results]
    # df["provincia"] = [str(r).split(",")[-4] for r in results]
    # df["nazione"] = [str(r).split(",")[-1] for r in results]

    # print(df[["regione", "user_location"]])

    print(df.columns)
    print(df.latitude)
    item = 0
    i = 0

    print(len(df))
    print(df.isnull().sum(axis=0))


    map = folium_map(df, names, title_map)
    map.save(os.path.join(os.getcwd(), 'Maps', f'{title_map}.html'))

