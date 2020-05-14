set -e

inputdir=$1
outputdir=$2
host=$3

mkdir -p ${outputdir}/tilejson

# Build unified tileset where each layer has different settings - e.g. zoom info.

# Build pedestrian network layer
tippecanoe -f -Z 6 -z 14 -B 14 -r 2.5 \
    -e ${outputdir}/sidewalkscore \
    ${inputdir}/sidewalkscore.geojson

cp /home/tippecanoe/sidewalkscore.json ${outputdir}/tilejson/sidewalkscore.json
sed -i s,HOSTNAME,${host},g ${outputdir}/tilejson/sidewalkscore.json
