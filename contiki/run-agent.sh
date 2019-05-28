DIRECTORY=$(cd `dirname $0` && pwd)
echo $DIRECTORY

cd $DIRECTORY
python mac_switching/agent.py --config config/wilab2/agent_config.yaml
