sums[3];

function sum()
{
    sums[0] += $2
    sums[1] += $3
    sums[2] += $4
}

function timestamp_fmt()
{
    $1 = strftime("%m/%d/%Y %I:%M:%S", $1)
}


{
    if ($5 == payment) {
        timestamp_fmt();
        sum();
        printf("%s %6.2f %6.2f %6.2f  %s\n", $1, $2, $3, $4, $5);
    }
}

END {
    printf("\nsubtotal: %7.2f\ntax:      %7.2f\ntotal:    %7.2f\n", sums[1], sums[2], sums[0]);
}