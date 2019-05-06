function datefilter(start, end) {
    return (start <= $1 && $1 <= end && $5)
}

function paymentfilter() {
    return ($5 == "Invoice")
}

BEGIN {
    FS = ",";
    printf("%s - %s\n\n",                 \
            strftime("%m/%d/%y", start), \
            strftime("%m/%d/%y", end))
}
{
    if (start <= $1             \
            && $1 <= end        \
            && $5 == "Invoice") {
        total += $2
    }
}

END {
    printf("Total: %.2f\n%s\n\n\n", total / 100, message)
}19