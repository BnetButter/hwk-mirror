BEGIN {
    FS = ","
    $1 = "Datetime";
    $2 = "Total";
    $3 = "Sub";
    $4 = "Tax";
    $5 = "Payment";
    printf("%-12s %s %5s %6s %9s\n", $1, $2, $3, $4, $5);
}
{
    printf("%s %6.2f %6.2f %6.2f   %s\n", $1, $2 / 100, $3 / 100, $4 / 100, $5)
}