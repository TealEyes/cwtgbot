from datetime import datetime, timezone
import pytz
from pyluach import dates, hebrewcal
from lunarcalendar import Converter, Solar

from util import hebrew_numeral
import sesDate

CW2_OFFSET = -11_093_806_800
CW3_OFFSET = -11_093_803_200
SPEED = 3

CW_MONTHS = ["Hailag", "Wintar", "Hornung", "Lenzin", "Ōstar", "Winni", "Brāh", "Hewi", "Aran", "Witu", "Wīndume", "Herbist", "Hailag", "Wintar"]
CW_PERIODS = ["Night", "Morning", "Day", "Evening", "Night"]
CW2_SEASONS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces", "Aries"]
CW3_SEASONS = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы", "Овен"]
CW2_WEEKDAYS = ["Mânotag", "Ziestag", "Mittawehha", "Jhonarestag", "Frîatag", "Sunnûnabund", "Sunnûntag", "Mânotag"]
CW3_WEEKDAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье", "Понедельник"]
HEB_MONTHS_ENG = ["Adar", "Nisan", "Iyyar", "Sivan", "Tammuz", "Av", "Elul", "Tishrei", "Marcheshvan", "Kislev", "Tevet", "Shevat", "Adar", "Adar"]
HEB_MONTHS_VRT = ["אדר", "ניסן", "אייר", "סיוון", "תמוז", "אב", "אלול", "תשרי", "מרחשוון", "כסלו", "טבת", "שבט", "אדר", "אדר"]
CLOCK_FACES = ["🕛", "🕧", "🕐", "🕜", "🕑", "🕝", "🕒", "🕞", "🕓", "🕟", "🕔", "🕠", "🕕", "🕡", "🕖", "🕢", "🕗", "🕣", "🕘", "🕤", "🕙", "🕥", "🕚", "🕦", "🕛"]

def emeryradio(user_data, command):
    output = []
    wkdyformat = ("%A")
    dateformat = ("%F")
    timeformat = ("%H:%M")
    secondsformat = ("%H:%M:%S")
    
    tzshown = { #this oughta come from some chat-specific settings or smth
        { pytz.timezone("US/Pacific"), "PST", "PDT", "San Francisco, San Diego" },
        { pytz.timezone("US/Eastern"), "EST", "EDT", "Boston, Augusta, Havana, Indianapolis" },
        { pytz.timezone("Etc/GMT"), "", "", "Accra" },
        { pytz.timezone("Europe/Zurich"), "CET", "CEST", "Amsterdam" },
        { pytz.timezone("Europe/Moscow"), "MSK", "MSK+1", "Moscow" },
        { pytz.timezone("Asia/Singapore"), "WPS", "", "Singapore, Manila, Hong Kong" },
        { pytz.timezone("Pacific/Auckland"), "NZST", "NZDT", "Kirikiriroa" }
    }

    adjustment2 = -37.0 #should be admin settings for this, as we may find these need adjusting
    adjustment3 = -37.0
    #utcdt = datetime(2019,2,1,17,22,35,0,timezone.utc)
    utcdt = datetime.now(timezone.utc)
    cw2tdt = datetime.fromtimestamp(SPEED * (utcdt.timestamp() - CW2_OFFSET), tz=timezone.utc)
    cw3tdt = datetime.fromtimestamp(SPEED * (utcdt.timestamp() - CW3_OFFSET), tz=timezone.utc)
    cw2adt = datetime.fromtimestamp(cw2tdt.timestamp() + SPEED * adjustment2, tz=timezone.utc)
    cw3adt = datetime.fromtimestamp(cw3tdt.timestamp() + SPEED * adjustment3, tz=timezone.utc)
    
    usertz = user_data.get('timezone')
    worktz = usertz if usertz else pytz.timezone("Etc/GMT")
    
    heb = dates.HebrewDate.from_pydate(utcdt.astimezone(worktz))
    yin = Converter.Solar2Lunar(Solar(utcdt.astimezone(worktz).year, utcdt.astimezone(worktz).month, utcdt.astimezone(worktz).day))
    ses = sesDate.sesDate(utcdt.timestamp(), utcdt.astimezone(worktz).utcoffset().total_seconds())

    sunmoon = "🌞" if (6 < cwadt.hour < 18) else ("🌚" if (yin.day < 3) else "🌙")
    timeToPeriodChange = (-(cwadt.timestamp() % 21600) + 21600) / 3
    timeToBattle = (-((cwtdt.timestamp() - 21600) % 86400) + 86400) / 3
    timeToArena = (-((cwtdt.timestamp() + 51300) % 259200) + 259200) / 3

    #if command == 2 then print CW2 stuff. else if command == 3 then CW3 stuff. else malformed
    
    output.append("<b>Current time</b>:")
    output.append(f'{CW_WEEKDAYS[int(cwadt.weekday())]} {cwadt.strftime(dateformat + ' ' + secondsformat)} (estimated)')
    output.append(f'{CW_WEEKDAYS[int(cwtdt.weekday())]} {cwtdt.strftime(secondsformat)} (tabular)')
    output.append(f'{sunmoon} {CW_PERIODS[int(cwadt.hour/6)]}: next change in ≈{int(timeToPeriodChange/3600)}h {int((timeToPeriodChange%3600)/60)}′ {int(timeToPeriodChange%60)}″')
    output.append(f'⚔ next battle in {int(timeToBattle/3600)}h {int((timeToBattle%3600)/60)}′ {int(timeToBattle%60)}″')
    output.append(f'📯 arena resets in {int(timeToArena/3600)}h {int((timeToArena%3600)/60)}′ {int(timeToArena%60)}″')
    output.append(f'this month: {cwMonthNames[int(cwadt.month)]}')
    output.append(f'next month: {cwMonthNames[int(cwadt.month)+1]}{"("+str(cwadt.year+1)+")" if cwadt.month == 12 else ""}')
    output.append('')

    pacificD = 'D' if (utcdt.astimezone(PT).utcoffset().total_seconds() == -25200) else 'S'
    mountainD = 'D' if (utcdt.astimezone(MT).utcoffset().total_seconds() == -21600) else 'S'
    centralD = 'D' if (utcdt.astimezone(CT).utcoffset().total_seconds() == -18000) else 'S'
    easternD = 'D' if (utcdt.astimezone(ET).utcoffset().total_seconds() == -14400) else 'S'
    europeanS = 'S' if (utcdt.astimezone(CET).utcoffset().total_seconds() == 7200) else ''
    
    #for i in tzshown
                  
    output.append(f'{utcdt.astimezone(PT).strftime("%A %F %H:%M.%S")} P{pacificD}T (UTC standard)')
    output.append(f"  ╰ GMT−{8 - (pacificD == 'D')}: San Francisco, San Diego")
    output.append(f'{utcdt.astimezone(ET).strftime("%A %H:%M")} E{easternD}T')
    output.append(f"  ╰ GMT−{5 - (easternD == 'D')}: Boston, Augusta, Havana")
    output.append(f'{utcdt.astimezone(GMT).strftime("%A %H:%M")} GMT')
    output.append("  ╰ GMT±0: Accra")
    output.append(f'{utcdt.astimezone(CET).strftime("%A %H:%M")} CE{europeanS}T')
    output.append(f"  ╰ GMT+{1 + (europeanS == 'S')}: Amsterdam, Bern")
    output.append(f'{utcdt.astimezone(WPS).strftime("%A %H:%M")} WPS')
    output.append("  ╰ GMT+8: Singapore, Manila, Hong Kong")
    output.append('')

    output.append(f"Equivalent dates (in P{pacificD}T; dates change at midnight)")
    output.append(f'{heb.year} {hebMonthNames[heb.month]}{" I" if hebrewcal.Year(heb.year).leap and heb.month > 11 else ""}{"I" if (hebrewcal.Year(heb.year).leap and heb.month == 13) else ""} {heb.day}' +
                  f' ({hebrew_numeral(heb.day)} {hebMonthNamesIvrit[heb.month]}{(" ב" if heb.month == 13 else " א") if hebrewcal.Year(heb.year).leap and heb.month > 11 else ""} {hebrew_numeral(heb.year)})')
    output.append(f'{yin.year+2698}/{yin.year+2638}年{yin.month}月{yin.day}日')
    output.append(f'{ses.natural.year:0>5d}.{ses.natural.season:0>1d}.{ses.natural.day:0>2d} (cyclic: {ses.cyclic.great}.{ses.cyclic.small}.{ses.cyclic.year}:{ses.cyclic.season}.{ses.cyclic.week}.{ses.cyclic.day})')

    return '\n'.join(output)

if __name__ == '__main__':
    print(emeryradio())
