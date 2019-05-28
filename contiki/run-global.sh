DIRECTORY=$(cd `dirname $0` && pwd)
echo $DIRECTORY

cd $DIRECTORY
python3 mac_switching/global_cp.py --config config/wilab2/global_cp_config.yaml --nodes config/wilab2/nodes.yaml
