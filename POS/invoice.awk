BEGIN {
    FS = ",";
    printf("%s - %s\n\n",                 \
            strftime("%m/%d/%y", start), \
            strftime("%m/%d/%y", end))
}

{
    if (start <= $1             \
            && $1 <= end        \
            && $5 == payment_type) {
        total += $2
    }
}

END {
    printf("Payment Type: %s\n", payment_type);
    printf("Total: %.2f\n%s\n\n\n", total / 100, message)
}