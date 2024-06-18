-- SELECT [Id]
--       ,[ExpeditorId]
--       ,[CustomerId]
--       ,[TimeStamp]
--       ,[ServerTimeStamp]
--       ,[Status]
--       ,[DockNo]
--   FROM [Orders].[dbo].[ExpeditorCheckouts]
--   where CAST([ServerTimeStamp] AS DATE) = 
--   cast(getDATE() as date);

-- INSERT into [Orders].[dbo].[ExpeditorCheckouts] 
--     ([ExpeditorId]
--       ,[CustomerId]
--       ,[TimeStamp]
--       ,[ServerTimeStamp]
--       ,[Status]
--       ,[DockNo])
-- values 
--     ('    7O   ', '   UAUSC ', '2024-05-29 16:51:17.997', '2024-05-29 16:51:17.997', 'S', 'SPO0000324294');

MERGE INTO [ExpeditorCheckouts] AS target
USING (VALUES ('    7O   ', '   UAUSC ', '2024-05-29 16:51:17.997', 'R', 'SPO0000324295')) AS source ([ExpeditorId], [CustomerId], [TimeStamp], [Status], [DockNo])
ON target.ExpeditorId = source.ExpeditorId
   AND target.CustomerId = source.CustomerId
   AND target.TimeStamp = source.TimeStamp
   AND target.DockNo = source.DockNo
WHEN MATCHED THEN
  UPDATE SET
    target.Status = source.Status,
    target.TimeStamp = source.TimeStamp
WHEN NOT MATCHED THEN
  INSERT ([ExpeditorId], [CustomerId], [TimeStamp], [ServerTimeStamp], [Status], [DockNo])
  VALUES ('    7O   ', '   UAUSC ', '2024-05-29 16:51:17.997', GETDATE(), 'R', 'SPO0000324295');
