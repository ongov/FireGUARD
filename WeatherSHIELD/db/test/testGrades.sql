use hindcast
go
    DECLARE @NumberMonths AS int
    DECLARE @OffsetMonths AS int
    DECLARE @MinRatioScore AS float
    SET @NumberMonths = 5
    SET @OffsetMonths = 0
    SET @MinRatioScore = .7
    SELECT
        h.[Generated],
        h.[Year],
        @NumberMonths AS NumberMonths,
        s.START_FROM,
        AVG(s.[Value]) AS AVG_VALUE,
        SUM(MONTH_GRADE) AS GRADE,
        SUM(MONTH_GRADE)/SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) AS GRADE2,
--        SUM(MONTH_GRADE)/(SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH))) AS GRADE3,
        (SUM(MONTH_GRADE) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))/(SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH))) AS GRADE3,
        (SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))/(SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH))) AS MAX_GRADE3,
        --~ 1 + LOG((SUM(MONTH_GRADE) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))/(SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))) AS GRADE2,
        --~ 1 + LOG((SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))/(SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))) AS GRADE3,
        --~ 1 + LOG((SUM([HINDCAST].[FCT_GradeHistoric](.99, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))/(SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))) AS GRADE4,
        --~ 1 + LOG((SUM([HINDCAST].[FCT_GradeHistoric](.98, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))/(SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))) AS GRADE5,
        --~ 1 + LOG((SUM([HINDCAST].[FCT_GradeHistoric](.97, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))/(SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))) AS GRADE6,
        --~ 1 + LOG((SUM([HINDCAST].[FCT_GradeHistoric](.96, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))/(SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) - SUM([HINDCAST].[FCT_GradeHistoric](@MinRatioScore, WHICH_MONTH)))) AS GRADE7,
        SUM([HINDCAST].[FCT_GradeHistoric](1, WHICH_MONTH)) AS MAX_GRADE,
        SUM([HINDCAST].[FCT_GradeHistoric](0, WHICH_MONTH)) AS MIN_GRADE
    FROM
    (
        SELECT DISTINCT [Year]
        FROM [HINDCAST].[DAT_Model]
    ) m
    CROSS APPLY
    (
        --~ SELECT
            --~ *
        --~ FROM [HINDCAST].[VIEW_HistoricMatch]
        --~ WHERE [Year]=m.[Year]
        SELECT
            h2.[Generated],
            m2.[Year],
            m2.[Month],
            m2.[Value],
            DATEADD(YYYY, [Year]-1900, DATEADD(MM, [Month]-1, 0)) AS FAKE_DATE
        FROM 
            [HINDCAST].[DAT_Historic] h2
            LEFT JOIN [HINDCAST].[DAT_HistoricMatch] m2 ON h2.[HistoricGeneratedId]=m2.[HistoricGeneratedId]
        WHERE [Year]=m.[Year]
    ) h
    CROSS APPLY
    (
        SELECT
            DATEADD(MM, @OffsetMonths, h.[FAKE_DATE]) AS START_FROM,
            [HINDCAST].[FCT_GradeHistoric]([Value], (DATEDIFF(MM, DATEADD(MM, @OffsetMonths, h.[FAKE_DATE]), FAKE_DATE) + @OffsetMonths)) AS MONTH_GRADE,
            Value,
            h.[FAKE_DATE] AS DD,
            DATEADD(MM, @OffsetMonths, h.[FAKE_DATE]) as D2,
            (DATEDIFF(MM, DATEADD(MM, @OffsetMonths, h.[FAKE_DATE]), FAKE_DATE) + @OffsetMonths) AS WHICH_MONTH,
            --DATEADD(MM, (DATEDIFF(MM, DATEADD(MM, @OffsetMonths, h.[FAKE_DATE]), FAKE_DATE)), DATEADD(MM, @OffsetMonths, h.[FAKE_DATE])) as FOR_MONTH,
            FAKE_DATE as FOR_MONTH
        FROM
            --~ [HINDCAST].[VIEW_HistoricMatch]
            (
                SELECT
                    hv2.[Generated],
                    mv2.[Year],
                    mv2.[Month],
                    mv2.[Value],
                    DATEADD(YYYY, [Year]-1900, DATEADD(MM, [Month]-1, 0)) AS FAKE_DATE
                FROM 
                    [HINDCAST].[DAT_Historic] hv2
                    LEFT JOIN [HINDCAST].[DAT_HistoricMatch] mv2 ON hv2.[HistoricGeneratedId]=mv2.[HistoricGeneratedId]
                WHERE
                    hv2.[Generated]=h.[Generated]
            ) hv
        WHERE
            [FAKE_DATE] >= DATEADD(MM, @OffsetMonths, h.[FAKE_DATE])
            -- not <= because that would be @NumberMonths + 1 months
            AND [FAKE_DATE] < DATEADD(MM, @NumberMonths, DATEADD(MM, @OffsetMonths, h.[FAKE_DATE]))
    ) s
    WHERE MONTH(FAKE_DATE)=MONTH(GETDATE())
    GROUP BY h.[Generated], h.[Year], s.START_FROM
ORDER BY h.[Generated], [GRADE] DESC