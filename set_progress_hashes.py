import math
import json

progress_types = ["rank_progress", "ownership_progress", "acadamy_progress"]

def convert_percent_to_progress_bar(percent, total_hashes=25):
    done = math.ceil(percent / 100 * total_hashes)
    open = total_hashes - done
    return done * "#", open * "#" 

def input_acadamy_progress():
    want_to_change = input("do you want to update htb acadamy progress? [y/n]: ")
    if want_to_change != "y":
        print("Not changing acadamy progress")
        return None
    acadamy_new_percent = input("Enter current acadamy progress in percent e.g.(22.5): ")
    try:
        acadamy_new_percent_float = float(acadamy_new_percent)
        return acadamy_new_percent_float
    except:
        print("please enter float value like 45.1")
        return None

def setup_data():
    new_data_list = []
    with open("./_data/htb_stats.json", "r") as htb_json:
        htb_data = json.load(htb_json)
    new_data_list.append(htb_data["profile"]["current_rank_progress"])
    new_data_list.append(htb_data["profile"]["rank_ownership"])
    acadamy_data = input_acadamy_progress()
    if acadamy_data:
        new_data_list.append(acadamy_data)
    else:
        new_data_list.append("")

    return new_data_list 


def set_new_progress_data(new_data_list):
    with open("./_data/htb_progressbar.json", "r") as htb_progress_file:
        progress_data = json.load(htb_progress_file)

    for progress, new_data in zip(progress_types, new_data_list):
        done_hashes, open_hashes = convert_percent_to_progress_bar(new_data)

        progress_data[progress]["done_hash_cnt"] = done_hashes
        progress_data[progress]["open_hash_cnt"] = open_hashes
        progress_data[progress]["value"] = float(new_data)


    with open("./_data/htb_progressbar.json", "w+") as htb_progress_write_file:
        progress_data = json.dump(progress_data, htb_progress_write_file)


def main():
    new_data = setup_data()
    set_new_progress_data(new_data)


if __name__ == "__main__":
    main()
