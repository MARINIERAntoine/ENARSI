import csv, ipaddress
from jinja2 import Environment, FileSystemLoader


def get_list_of_devices(dictreader: list):
    devices_list = []
    for item in dictreader:
        if item["Device-ID"] not in devices_list:
            devices_list.append(item["Device-ID"])
    return devices_list


def get_ipv4_address(subnet: ipaddress.IPv4Network, device_id: str):
    return str(list(subnet.hosts())[int(device_id)]) + " " + str(subnet.netmask)


def get_ipv6_address(subnet: ipaddress.IPv6Network, device_id: str):
    return str(subnet).replace("/64", "{}/64".format(device_id))


def get_neighbor(subnet: str, device_id: str):
    if subnet == "4.4.4.0/24":
        return "WAN Router"
    elif subnet == "100.0.2.0/24":
        return "Switch OSPF AREA 11"
    else:
        split_subnet = subnet.split("/")[0].split(".")
        devices_connected_id = [split_subnet[1], split_subnet[2]]
        devices_connected_id.remove(device_id)
        return "R" + devices_connected_id[0]


if __name__ == "__main__":
    with open("Subnets.csv") as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=",")
        reader_list = list(spamreader)
        devices_list = get_list_of_devices(reader_list)
        for device_id in devices_list:
            interfaces_list = []
            for row in reader_list:
                if device_id == row["Device-ID"]:
                    interfaces_list.append(
                        {
                            "interface": "GigabitEthernet0/{}".format(row["Interface"]),
                            "ipv4_address": get_ipv4_address(
                                ipaddress.ip_network(row["Subnet IPv4"]), device_id
                            ),
                            "ipv6_address": get_ipv6_address(
                                ipaddress.ip_network(row["Subnet IPv6"]), device_id
                            ),
                            "neighbor": get_neighbor(row["Subnet IPv4"], device_id),
                        }
                    )
            print(interfaces_list)
            env = Environment(loader=FileSystemLoader("templates"))
            tpl = env.get_template("configuration_template.txt")
            output = tpl.render(device_id=device_id, interfaces_list=interfaces_list)
            with open(
                "./startup_confs/R{}.txt".format(device_id), "w"
            ) as configuration_file:
                configuration_file.write(output)
