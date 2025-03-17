CREATE TABLE [dbo].[macro_user_groups] (
    [Date] DATETIME NOT NULL,  -- 분석 날짜
    [All_user] INT NOT NULL,  -- 전체 유저 수
    [All_group] INT NOT NULL,  -- 전체 그룹 수
    [Multi_user_group] INT NOT NULL,  -- 다중 유저 그룹 수
    [Multi_user_group_all_user] INT NOT NULL,  -- 다중 유저 그룹에 속한 전체 유저 수
    PRIMARY KEY ([Date])
);
GO

-- Date: 분석한 날짜
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Analysis date', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'macro_user_groups', 
  @level2type=N'COLUMN', 
  @level2name=N'Date';
  
-- All_user: 전체 유저 수
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Total number of users', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'macro_user_groups', 
  @level2type=N'COLUMN', 
  @level2name=N'All_user';

-- All_group: 전체 그룹 수
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Total number of groups', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'macro_user_groups', 
  @level2type=N'COLUMN', 
  @level2name=N'All_group';

-- Multi_user_group: 다중 유저 그룹 수
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Number of multi-user groups', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'macro_user_groups', 
  @level2type=N'COLUMN', 
  @level2name=N'Multi_user_group';

-- Multi_user_group_all_user: 다중 유저 그룹에 속한 전체 유저 수
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Total number of users in multi-user groups', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'macro_user_groups', 
  @level2type=N'COLUMN', 
  @level2name=N'Multi_user_group_all_user';
