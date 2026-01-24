/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/rip-helper.h"
#include "ns3/flow-monitor-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("RipModifiedNetwork");

int
main (int argc, char *argv[])
{
  Time::SetResolution (Time::NS);
  LogComponentEnable ("RipModifiedNetwork", LOG_LEVEL_INFO);

  
  Ptr<Node> A = CreateObject<Node> ();
  Ptr<Node> B = CreateObject<Node> ();
  Ptr<Node> C = CreateObject<Node> ();
  Ptr<Node> D = CreateObject<Node> ();
  Ptr<Node> E = CreateObject<Node> ();

  NodeContainer allNodes (A, B, C, D, E);


  RipHelper rip;
  InternetStackHelper internet;
  internet.SetRoutingHelper (rip);
  internet.Install (allNodes);

 
  PointToPointHelper p2p;
  p2p.SetDeviceAttribute ("DataRate", StringValue ("5Mbps"));


  p2p.SetChannelAttribute ("Delay", StringValue ("1ms"));
  NetDeviceContainer dAB = p2p.Install (A, B);


  NetDeviceContainer dAE = p2p.Install (A, E);


  p2p.SetChannelAttribute ("Delay", StringValue ("2ms"));
  NetDeviceContainer dEC = p2p.Install (E, C);


  p2p.SetChannelAttribute ("Delay", StringValue ("1ms"));
  NetDeviceContainer dAC = p2p.Install (A, C);

  p2p.SetChannelAttribute ("Delay", StringValue ("5ms"));
  NetDeviceContainer dBC = p2p.Install (B, C);

  // B -- D (cost 6)
  p2p.SetChannelAttribute ("Delay", StringValue ("6ms"));
  NetDeviceContainer dBD = p2p.Install (B, D);

  // C -- D (cost 1)
  p2p.SetChannelAttribute ("Delay", StringValue ("1ms"));
  NetDeviceContainer dCD = p2p.Install (C, D);


  Ipv4AddressHelper ipv4;

  ipv4.SetBase ("10.0.1.0", "255.255.255.0");
  ipv4.Assign (dAB);

  ipv4.SetBase ("10.0.2.0", "255.255.255.0");
  ipv4.Assign (dAE);

  ipv4.SetBase ("10.0.3.0", "255.255.255.0");
  ipv4.Assign (dEC);

  ipv4.SetBase ("10.0.4.0", "255.255.255.0");
  ipv4.Assign (dAC);

  ipv4.SetBase ("10.0.5.0", "255.255.255.0");
  ipv4.Assign (dBC);

  ipv4.SetBase ("10.0.6.0", "255.255.255.0");
  ipv4.Assign (dBD);

  ipv4.SetBase ("10.0.7.0", "255.255.255.0");
  ipv4.Assign (dCD);


  uint16_t port = 4000;

  UdpServerHelper server (port);
  ApplicationContainer serverApps = server.Install (D);
  serverApps.Start (Seconds (1.0));
  serverApps.Stop (Seconds (20.0));

  UdpClientHelper client (Ipv4Address ("10.0.7.2"), port);
  client.SetAttribute ("MaxPackets", UintegerValue (100));
  client.SetAttribute ("Interval", TimeValue (Seconds (0.5)));
  client.SetAttribute ("PacketSize", UintegerValue (512));

  ApplicationContainer clientApps = client.Install (A);
  clientApps.Start (Seconds (2.0));
  clientApps.Stop (Seconds (20.0));

  
  p2p.EnablePcapAll ("rip-simple-network");

 
  FlowMonitorHelper flowmon;
  Ptr<FlowMonitor> monitor = flowmon.InstallAll ();

  Simulator::Stop (Seconds (20.0));
  Simulator::Run ();

  monitor->SerializeToXmlFile ("rip-simple-network.flowmon", true, true);

  Simulator::Destroy ();
  return 0;
}
