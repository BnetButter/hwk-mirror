BEGIN {
    FS = ",";
    printf("%s - %s\n\n",                 \
            strftime("%m/%d/%y", start), \
            strftime("%m/%d/%y", end))
}

{
    if (start <= $1             \
            && $1 <= end) {       \

        if ($5 == "Cash")
            cash_total += $2
        else if ($5 == "Invoice")
            invoice_total += $2
        else if ($5 == "Check")
            check_total += $2
            
        total += $2
        subtotal += $3
        tax += $4
    }
}

END {
    
    printf("Cash total\n    $%.2f\n", cash_total / 100)
    printf("Invoice total\n    $%.2f\n", invoice_total / 100)
    printf("Check total\n    $%.2f\n", check_total / 100)
    print "\nCombined"
    printf("subtotal : $%.2f\n", subtotal / 100)
    printf("tax      : $%.2f\n", tax / 100)
    printf("total    : $%.2f\n", total / 100)
    printf("\n\n\n\n")
}

# end = 1558137600
# start = 1558051200