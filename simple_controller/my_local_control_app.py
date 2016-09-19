import logging
import datetime
import random
import wishful_upis as upis
from wishful_agent.core import wishful_module
from wishful_agent.timer import TimerEventSender
from common import AveragedSpectrumScanSampleEvent
from common import StartMyFilterEvent
from common import StopMyFilterEvent

__author__ = "Piotr Gawlowicz"
__copyright__ = "Copyright (c) 2016, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gawlowicz}@tkn.tu-berlin.de"


class PeriodicEvaluationTimeEvent(upis.mgmt.TimeEvent):
    def __init__(self):
        super().__init__()


@wishful_module.build_module
class MyController(wishful_module.ControllerModule):
    def __init__(self):
        super(MyController, self).__init__()
        self.log = logging.getLogger('MyController')
        self.running = False
        self.nodes = []

        self.timeInterval = 10
        self.timer = TimerEventSender(self, PeriodicEvaluationTimeEvent)
        self.timer.start(self.timeInterval)

        self.myFilterRunning = False
        self.packetLossEventsEnabled = False

    @wishful_module.on_start()
    def my_start_function(self):
        print("start control app")
        self.running = True

        node = self.localNode
        self.log.info("My local node: {}, Local: {}"
                      .format(node.hostname, node.local))

        retVal = node.net.create_packetflow_sink(port=1234)
        print("Server started: {}".format(retVal))

        for dev in node.get_devices():
            print("Dev: ", dev.name)

        for m in node.get_modules():
            print("Module: ", m.name)

        for apps in node.get_apps():
            print("App: ", m.name)

        device = node.get_device(0)
        device.radio.set_power(15)
        device.radio.set_channel(random.randint(1, 11))
        device.enable_event(upis.radio.PacketLossEvent)
        self.packetLossEventsEnabled = True
        device.start_service(
            upis.radio.SpectralScanService(rate=1000, f_range=[2200, 2500]))

    @wishful_module.on_exit()
    def my_stop_function(self):
        print("stop control app")
        self.running = False

    @wishful_module.on_event(upis.radio.PacketLossEvent)
    def serve_packet_loss_event(self, event):
        node = event.node
        device = event.device
        self.log.info("Packet loss in node {}, dev: {}"
                      .format(node.hostname, device.name))

    @wishful_module.on_event(AveragedSpectrumScanSampleEvent)
    def serve_spectral_scan_sample(self, event):
        avgSample = event.avg
        self.log.info("Averaged Spectral Scan Sample: {}"
                      .format(avgSample))

    def default_cb(self, data):
        node = data.node
        devName = None
        if data.device:
            devName = data.device.name
        msg = data.msg
        print("Default Callback: "
              "Node: {}, Dev: {}, Data: {}"
              .format(node.hostname, devName, msg))

    def get_power_cb(self, data):
        node = data.node
        dev = data.device
        msg = data.msg
        print("Power in "
              "Node: {}, Dev: {}, was set to: {}"
              .format(node.hostname, dev.name, msg))

    @wishful_module.on_event(PeriodicEvaluationTimeEvent)
    def periodic_evaluation(self, event):
        # go over collected samples, etc....
        # make some decisions, etc...
        print("Periodic Evaluation")

        node = self.localNode
        device = node.get_device(0)

        self.log.info("My local node: {}, Local: {}"
                      .format(node.hostname, node.local))
        self.timer.start(self.timeInterval)

        if self.packetLossEventsEnabled:
            device.disable_event(upis.radio.PacketLossEvent)
            self.packetLossEventsEnabled = False
        else:
            device.enable_event(upis.radio.PacketLossEvent)
            self.packetLossEventsEnabled = True

        if self.myFilterRunning:
            self.send_event(StopMyFilterEvent())
            self.myFilterRunning = False
        else:
            self.send_event(StartMyFilterEvent())
            self.myFilterRunning = True

        # execute non-blocking function immediately
        device.blocking(False).radio.set_power(random.randint(1, 20))

        # execute non-blocking function immediately, with specific callback
        device.callback(self.get_power_cb).radio.get_power()

        # schedule non-blocking function delay
        node.delay(3).callback(self.default_cb).net.create_packetflow_sink(port=1234)

        # schedule non-blocking function exec time
        exec_time = datetime.datetime.now() + datetime.timedelta(seconds=3)
        newChannel = random.randint(1, 11)
        device.exec_time(exec_time).radio.set_channel(channel=newChannel)

        # execute blocking function immediately
        result = device.radio.get_channel()
        print("{} Channel is: {}".format(datetime.datetime.now(), result))

        # exception handling, clean_per_flow_tx_power_table implementation
        # raises exception
        try:
            device.radio.clean_per_flow_tx_power_table()
        except Exception as e:
            print("{} !!!Exception!!!: {}".format(
                datetime.datetime.now(), e))
