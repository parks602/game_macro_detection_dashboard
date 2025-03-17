CREATE TABLE [dbo].[login_logs](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[username] [nvarchar](255) NOT NULL,
	[login_time] [datetime] NULL,
	[status] [nvarchar](50) NOT NULL,
	[ip_address] [nvarchar](50) NULL,
	[user_agent] [nvarchar](255) NULL
	)
GO

-- id: 로그 식별자 (자동 증가)
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Unique identifier for the login log entry', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'login_logs', 
  @level2type=N'COLUMN', 
  @level2name=N'id';

-- username: 로그인한 사용자명
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Username of the user who attempted to log in', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'login_logs', 
  @level2type=N'COLUMN', 
  @level2name=N'username';

-- login_time: 로그인 시도 시간
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Timestamp of the login attempt', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'login_logs', 
  @level2type=N'COLUMN', 
  @level2name=N'login_time';

-- status: 로그인 결과 (성공/실패)
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Login attempt status (e.g., SUCCESS, FAILED)', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'login_logs', 
  @level2type=N'COLUMN', 
  @level2name=N'status';

-- ip_address: 로그인 시도한 IP 주소
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'IP address of the user during login attempt', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'login_logs', 
  @level2type=N'COLUMN', 
  @level2name=N'ip_address';

-- user_agent: 로그인 시 사용한 브라우저 및 디바이스 정보
EXEC sys.sp_addextendedproperty 
  @name=N'MS_Description', 
  @value=N'Browser or device information from which the login was attempted', 
  @level0type=N'SCHEMA', 
  @level0name=N'dbo', 
  @level1type=N'TABLE', 
  @level1name=N'login_logs', 
  @level2type=N'COLUMN', 
  @level2name=N'user_agent';
