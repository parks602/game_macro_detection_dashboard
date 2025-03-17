CREATE TABLE [dbo].[range_histogram] (
    [Date] DATETIME NOT NULL,  -- 분석 날짜
    [Range_Start] FLOAT NOT NULL,  -- 구간 시작 값
    [Range_End] FLOAT NOT NULL,  -- 구간 종료 값
    [Count] INT NOT NULL  -- 해당 구간 내 데이터 개수
);
GO

-- Date: 분석한 날짜
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Analysis date', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'range_histogram', 
  @level2type=N'COLUMN', 
  @level2name=N'Date';

-- Range_Start: 구간 시작 값
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Start value of the range', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'range_histogram', 
  @level2type=N'COLUMN', 
  @level2name=N'Range_Start';

-- Range_End: 구간 종료 값
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'End value of the range', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'range_histogram', 
  @level2type=N'COLUMN', 
  @level2name=N'Range_End';

-- Count: 해당 구간 내 데이터 개수
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Number of data points in the range', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'range_histogram', 
  @level2type=N'COLUMN', 
  @level2name=N'Count';
