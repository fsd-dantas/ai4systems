cmake_minimum_required(VERSION 3.16)
project(dual-homed-backhaul CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(ns3 REQUIRED COMPONENTS
    applications
    core
    flow-monitor
    internet
    lte
    mobility
    netanim
    network
    point-to-point
    propagation
    virtual-net-device
)

add_executable(dual-homed-backhaul dual-homed-backhaul.cc)
target_link_libraries(dual-homed-backhaul PRIVATE
    ns3::applications
    ns3::core
    ns3::flow-monitor
    ns3::internet
    ns3::lte
    ns3::mobility
    ns3::netanim
    ns3::network
    ns3::point-to-point
    ns3::propagation
    ns3::virtual-net-device
)
