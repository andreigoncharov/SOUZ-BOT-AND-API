# SELECT
#      CAST(SUBSTRING(j.DATE_TIME_IDDOC, 1, 8) AS DATETIME) as [DateTime]
#     ,e.id ExpeditorId
#     ,e.DESCR as Expeditor
#     ,p.sp294 as PhoneNumber
#     ,RTRIM(LTRIM(c.code)) CustomerId
#     ,c.DESCR as Customer
# -- ,i.sp1035 as Comment
#     ,CAST(SP1197 AS INT) [Order]
#     ,CAST(SP1797 AS INT) [Route]
#     ,drv.ID as DriverID
#     ,drv.DESCR as Driver
#     ,i.SP1408 as AgentID
#     ,managers.DESCR
#     ,chk.[TimeStamp]
#     ,chk.[DockNo]
# FROM [192.168.3.18].[SOUZ].dbo.[sc703] e
# INNER JOIN [192.168.3.18].[SOUZ].dbo.[dh640] i
#   ON i.SP702 = e.id
# inner join [192.168.3.18].[SOUZ].dbo.[sc284] p
# on e.sp705 = p.id
# INNER JOIN [192.168.3.18].[SOUZ].dbo.[_1SJOURN] j
#   ON j.iddoc = i.iddoc
#     AND j.CLOSED = 1
#     AND CAST(SUBSTRING(j.DATE_TIME_IDDOC, 1, 8) AS DATE) = CAST('20240404' AS date)--cast(getDATE() as date)
# INNER JOIN [192.168.3.18].[SOUZ].dbo.[sc137] c
#   ON c.ID = i.SP643
# INNER JOIN [192.168.3.18].[SOUZ].dbo.SC580 as drv
#   ON drv.ID = i.SP650
# INNER JOIN [192.168.3.18].[Souz].dbo.SC885 as managers
#   ON managers.ID = i.sp1408
# left JOIN ExpeditorCheckouts chk
#   ON chk.CustomerId = RTRIM(LTRIM(c.code)) AND
#      chk.ExpeditorId = e.id and
#      cast(chk.TimeStamp as DATE) = CAST('20240404' AS date)
# order by ExpeditorId, CAST(SP1797 AS INT), CAST(SP1197 AS INT)