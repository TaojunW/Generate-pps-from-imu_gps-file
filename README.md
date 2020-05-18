# Generate pps from imu_gps file
Based on previous imu_gps file and pps file, generate new pps file with new imu_gps file by interpolation.

1. Read the old imu_gps file and pps file
2. Find the average time delay of this UAV system
3. Got new imu_gps file with the same UAV system but missing pps file
4. Using interpolation and calcualted average time delay to generate a new pps file
