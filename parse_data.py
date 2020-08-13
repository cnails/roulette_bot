import csv
from math import ceil, floor


NUMBERS = [
    0, 26, 3, 35, 12, 28, 7, 29, 18, 22, 9, 31, 14,
    20, 1, 33, 16, 24, 5, 10, 23, 8, 30, 11, 36,
    13, 27, 6, 34, 17, 25, 2, 21, 4, 19, 15, 32,
]
ONE = 360 / 37
NUM_OF_CELLS = 12
START_ANGLE = 123.859459459


def closest_nums(angle):
    if angle < START_ANGLE:
        return (
            NUMBERS[-(NUM_OF_CELLS - floor(angle / ONE)) - 1],
            NUMBERS[-(NUM_OF_CELLS - floor(angle / ONE))],
            NUMBERS[-(NUM_OF_CELLS - ceil(angle / ONE))],
            NUMBERS[-(NUM_OF_CELLS - ceil(angle / ONE)) + 1],
        )
    else:
        return (
            NUMBERS[floor(angle / ONE) - NUM_OF_CELLS - 1],
            NUMBERS[floor(angle / ONE) - NUM_OF_CELLS],
            NUMBERS[ceil(angle / ONE) - NUM_OF_CELLS],
            NUMBERS[(ceil(angle / ONE) - NUM_OF_CELLS + 1) % len(NUMBERS)]
        )


def main():
    csvfile = open('data_train.csv', 'w', newline='')
    writer = csv.writer(
        csvfile, delimiter=','
    )
    writer.writerow(['start_angle', 'inner_wheel_time_around', 'ball_time_around', 'end_angle', 'end_number'])

    with open('predictions1.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if not line.strip():
                continue
            line = line.split(', ')
            time_ = float(line[0].split(': ')[1])
            start_number = int(line[1].split(': ')[1])
            end_number = int(line[2].split(': ')[1])
            start_angle = float(line[3].split(': ')[1])
            end_angle = float(line[4].split(': ')[1])
            inner_wheel_time_around = float(line[5].split(': ')[1])
            ball_time_around = float(line[6].split(': ')[1])
            # start_angle != 292.834 and end_angle != 292.834 and \
            if time_ < 10 and start_number in closest_nums(start_angle) and \
                    end_number in closest_nums(end_angle) and \
                    inner_wheel_time_around and ball_time_around:
                writer.writerow([start_angle, inner_wheel_time_around, ball_time_around, end_angle, end_number])
    csvfile.close()


if __name__ == '__main__':
    main()
