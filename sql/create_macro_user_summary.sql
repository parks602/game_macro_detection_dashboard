CREATE TABLE [dbo].[macro_user_summary] (
    [AID] INT NOT NULL,  -- ���� ID
    [Date] DATE NOT NULL,  -- ��� ��¥
    [distinction] NVARCHAR(20) NOT NULL CHECK ([distinction] IN ('detection', 'suspicion', 'block','normal')),  
    -- Ž�� ���� ('detection', 'suspicion', 'block' ���� ���)
    [reason] NVARCHAR(255) NULL  -- Ž�� ����
);
-- ���̺� ���� �߰�
EXEC sys.sp_addextendedproperty 
  @name = N'MS_Description', 
  @value = N'Macro user detection summary table', 
  @level0type = N'SCHEMA', 
  @level0name = N'dbo', 
  @level1type = N'TABLE', 
  @level1name = N'macro_user_summary';

-- AID: ���� ID
EXEC sys.sp_addextendedproperty 
  @name = N'MS_Description', 
  @value = N'User Account ID', 
  @level0type = N'SCHEMA',  
  @level0name = N'dbo', 
  @level1type = N'TABLE', 
  @level1name = N'macro_user_summary', 
  @level2type = N'COLUMN', 
  @level2name = N'AID';

-- Date: ��� ��¥
EXEC sys.sp_addextendedproperty 
  @name = N'MS_Description', 
  @value = N'Record date', 
  @level0type = N'SCHEMA', 
  @level0name = N'dbo', 
  @level1type = N'TABLE', 
  @level1name = N'macro_user_summary', 
  @level2type = N'COLUMN', 
  @level2name = N'Date';

-- distinction: Ž�� ����
EXEC sys.sp_addextendedproperty 
  @name = N'MS_Description', 
  @value = N'Detection category (detection, suspicion, block)', 
  @level0type = N'SCHEMA', 
  @level0name = N'dbo', 
  @level1type = N'TABLE', 
  @level1name = N'macro_user_summary', 
  @level2type = N'COLUMN', 
  @level2name = N'distinction';

-- reason: Ž�� ����
EXEC sys.sp_addextendedproperty 
  @name = N'MS_Description', 
  @value = N'Reason for detection', 
  @level0type = N'SCHEMA', 
  @level0name = N'dbo', 
  @level1type = N'TABLE', 
  @level1name = N'macro_user_summary', 
  @level2type = N'COLUMN', 
  @level2name = N'reason';
