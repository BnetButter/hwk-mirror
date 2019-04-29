function gettimestamp(string)
{
    time[2];
    split(string, time, " ");
    datesplit[3];
    timesplit[3];

    split(time[1], datesplit, "/");
    split(time[2], timesplit, ":")

    year = datesplit[3] + 2000

    result1 = sprintf("%d %02d %02d", year, datesplit[1], datesplit[2]);
    result2 = sprintf("%02d %02d %02d", timesplit[1], timesplit[2], timesplit[3]);
    timefmt = sprintf("%s %s", result1, result2);
    print(mktime(timefmt));
    return mktime(timefmt);
}

function datefilter(field, start, end)
{
    
    if (end) 
        return start <= field && field <= end    
    else 
        return start <= field
}

BEGIN {
    FS = ",";

    
    start = gettimestamp(start);
    end = gettimestamp(end);
    if (start > end)
        print "end date is before start date";
}

{
    if (datefilter($1, start, end))
        printf("%d %6.2f %6.2f %6.2f   %s\n", $1, $2 / 100, $3 / 100, $4 / 100, $5)
}

END {}