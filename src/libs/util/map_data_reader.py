
def read_supply_node_file(file_path:str) -> tuple:
    with open(file_path,"r",encoding="utf-8") as file:
        result = list()
        for line in file:
            province = line.strip().split(" ")[1]
            result.append(province)
    
    return tuple(result)

def read_railway_file(file_path:str) -> tuple:
    with open(file_path,"r",encoding="utf-8") as file:
        result = list()
        for line in file:
            single_railway_data = line.strip().split(" ")
            railway_level = single_railway_data[0]
            railway_provinces = tuple(single_railway_data[2:len(single_railway_data)])
            result.append({"level":railway_level,
                           "province":railway_provinces})
    return tuple(result)